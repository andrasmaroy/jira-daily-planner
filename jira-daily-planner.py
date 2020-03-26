from datetime import date
from dateutil.parser import isoparse
from dateutil.relativedelta import relativedelta
from jira import JIRA
from pconf import Pconf

import re


Pconf.env(
    match="^JIRA_.*",
    docker_secrets=["JIRA_PASSWORD_FILE"],
    to_lower=True,
    convert_underscores=True
)
Pconf.defaults({
    "jira-template-type": "Template Task",
    "jira-target-type": "Task",
    "jira-project-key": "DAILY",
    "jira-created-state": "Backlog",
    "jira-done-state": "Done",
    "jira-field-name": "Repeat"

})
config = Pconf.get()

jira = JIRA(config["jira-url"], basic_auth=(config["jira-user"], config["jira-password"]))


def has_open_clone(template, status):
    jql = 'project = {} AND type = "{}" AND issueLinkType = clones AND issuekey in linkedIssues("{}") AND status = "{}"'
    clones = jira.search_issues(jql.format(config["jira-project-key"], config["jira-target-type"], template.key, status))
    return len(clones) > 0


def get_clone_close_date(template):
    jql = 'project = {} AND type = "{}" AND issueLinkType = clones AND issuekey in linkedIssues("{}") AND status = "{}"'
    issues = jira.search_issues(jql.format(config["jira-project-key"], config["jira-target-type"], template.key, config["jira-done-state"]))
    return issues[0].fields.resolutiondate


def get_clone_creation_date(template):
    jql = 'project = {} AND type = "{}" AND issueLinkType = clones AND issuekey in linkedIssues("{}") ORDER BY createdDate DESC'
    issues = jira.search_issues(jql.format(config["jira-project-key"], config["jira-target-type"], template.key))
    return issues[0].fields.created


def get_repeat_field_id():
    fields = jira.fields()
    for field in fields:
        if field["name"] == config["jira-field-name"]:
            return field["id"]


def get_repeat_date(refdate, repeat):
    if (interval := re.match('(\d+)d', repeat)):
        return refdate + relativedelta(days=+int(interval.group(1)))
    elif (interval := re.match('(\d+)w', repeat)):
        return refdate + relativedelta(weeks=+int(interval.group(1)))
    elif (interval := re.match('(\d+)m', repeat)):
        return refdate + relativedelta(months=+int(interval.group(1)))
    elif (interval := re.match('(\d+)y', repeat)):
        return refdate + relativedelta(years=+int(interval.group(1)))


def should_create_today(createddate, resolutiondate, repeat):
    if repeat.startswith("OnComplete"):
        return get_repeat_date(resolutiondate, repeat[11:]) == date.today()
    else:
        return get_repeat_date(createddate, repeat) == date.today()


def clone_issue(template):
    issue_dict = {
        "project": {"key": config["jira-project-key"]},
        "summary": template.fields.summary,
        "issuetype": {"name": config["jira-target-type"]},
    }
    new_issue = jira.create_issue(fields=issue_dict)
    jira.create_issue_link("Cloners", new_issue, template)


repeat_field_id = get_repeat_field_id()
templates = jira.search_issues('project={} AND type="{}"'.format(config["jira-project-key"], config["jira-template-type"]))
for t in templates:
    if not has_open_clone(t, config["jira-created-state"]):
        if has_open_clone(t, config["jira-done-state"]):
            created = isoparse(get_clone_creation_date(t))
            resolutiondate = isoparse(get_clone_close_date(t))
            cmd = "t.fields." + repeat_field_id
            if should_create_today(created, resolutiondate, eval(cmd)):
                print("Template '{}' is repeating today, creating clone".format(t.key))
                clone_issue(t)
            else:
                print("Template '{}' doesn't repeate today".format(t.key))
                continue
        else:
            print("Creating first clone of '{}'".format(t.key))
            clone_issue(t)
    else:
        print("Template '{}' has alreay an open clone".format(t.key))
        continue
