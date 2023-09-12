import json
import sys

import requests

from models import MigrationLog

slack_web_hook = "slack_web_hook"


def send_migration_slack(log: MigrationLog):
    """
    연동된 슬랙 채널에 Exception 발생 내용 알림을 보내는 함수
    :param log:
    :return:
    """
    url = slack_web_hook

    try:
        title = f":zap:*Exception Notification*"  # 타이틀 입력

        message = f"*{title}\n"
        if log.id:
            message += f"*log_id*: {log.id}\n"
        if log.title:
            message += f"*title*: {log.title}\n"
        if log.reference_type and log.reference_id:
            message += f"*{log.reference_type}_id*: {log.reference_id}\n"
        if log.status:
            message += f"*status*: {log.status}\n"
        if log.description:
            message += f"*description*: {log.description}\n"
        if log.result:
            message += f"*result*: {log.result}\n"
        if log.err_msg:
            message += f"*err_msg*: {log.err_msg}\n"

        slack_data = {
            "username": "backend.python",
            "icon_emoji": "sunglasses:",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": message
                    }
                }
            ]
        }
        byte_length = str(sys.getsizeof(slack_data))
        headers = {'Content-Type': "application/json", 'Content-Length': byte_length}

        response = requests.post(url, data=json.dumps(slack_data), headers=headers)
        if response.status_code != 200:
            raise Exception(response.status_code, response.text)

    except Exception as exc:
        # slack 오류시에도 서비스에 영향을 주면 안됨
        pass
