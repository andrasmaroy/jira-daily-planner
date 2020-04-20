FROM python:3.8-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN apk add gcc libffi-dev musl-dev openssl-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del gcc libffi-dev musl-dev openssl-dev

COPY jira-daily-planner.cron /etc/cron.d/jira-daily-planner
RUN chmod 0644 /etc/cron.d/jira-daily-planner
RUN crontab /etc/cron.d/jira-daily-planner

COPY jira-daily-planner.py ./

CMD ["crond", "-f"]
