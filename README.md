# jira-daily-planner

The goal of this script is to recreate certain tasks in a Jira project every day. Designed to be ran with a cron job each day.

In the given project it expects an issue type to use as templates and another one to use as actual tasks.
In the template tasks the interval with which the tasks are expected to repeat, is to bet set in a specific field (`Repeat` by default).
According to the interval a task is created and linked to its template as a clone.

The repeat interval can be prepended with the `OnComplete` keyword which will make the script count the interval from the latest closed task instead of the latest creation date.

For the interval the format is a number followed by either `d`, `w`, `m` or `y` for day, week, month and year respectively.

If there is a task for the given template still open and the repeat schedule is due that day the task won't be created again.

## Examples
Consider a template task "Water the plants" that you want to do every 3 days, but to avoid over-watering your plants if you miss one day you want to do it only 3 days after you've actually watered them. To do this you could set the repeat field to `OnComplete 3d`

Consider something you want to do everyday, just set the repeat field to `1d`, it will be recreated each day.

## Prerequisites
* Python 3.8
* A Jira project obviously

## Configuration
The script uses the following environment variables for configuration
| Variable           | Content                            | Default       |
| ------------------ | ---------------------------------- | ------------- |
| JIRA_URL           | Jira server url                    |               |
| JIRA_USER          | User to connect with               |               |
| JIRA_PASSWORD      | Password for said user             |               |
| JIRA_TEMPLATE_TYPE | Issue type to use as template      | Template Task |
| JIRA_TARGET_TYPE   | Issue type for the created issues  | Task          |
| JIRA_PROJECT_KEY   | Jira project key to use            | DAILY         |
| JIRA_CREATED_STATE | Issue state upon creation          | Backlog       |
| JIRA_DONE_STATE    | Issue state when closed            | Done          |
| JIRA_FIELD_NAME    | Field name to use for the interval | Repeat        |

## Usage

First install the dependencies (preferably in a [virtualenv](https://docs.python.org/3/library/venv.html#venv-def)):
```bash
pip install -r requirements.txt
```

Set the above environment variables according to your environment / Jira setup, then run:
```bash
python jira-daily-planner.py
```

If everything was set correctly you should see the newly created tasks on your board.
