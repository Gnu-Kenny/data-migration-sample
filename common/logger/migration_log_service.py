from sqlalchemy.orm import Session

from models import MigrationLog
from common.type.ResultType import ResultType
from common.type.StatusType import StatusType
from common.util.slack_util import send_migration_slack


def change_log(log: MigrationLog, status: StatusType = None, description=None, err_msg=None,
               result: ResultType = None):
    if status is not None:
        log.status = status.code
    if description is not None:
        log.description = description
    if err_msg is not None:
        log.err_msg = err_msg
    if result is not None:
        log.result = result.code

    if result and result == result.FAIL:
        send_migration_slack(log)

    log.save
    return log


def get_or_create_migration_log(db_conn: Session, reference_id: int, reference_type: str, title: str):
    migration_log: MigrationLog = MigrationLog(
        reference_id=reference_id,
        reference_type=reference_type,
        title=title
    )

    prev_migration_log: MigrationLog = migration_log.load_with_reference_and_title

    if prev_migration_log.id is not None:
        prev_migration_log.status = StatusType.READY.code
        prev_migration_log.result = ResultType.UNKNOWN.code

        prev_migration_log.save
        return prev_migration_log

    migration_log_id = migration_log.insert_one()
    migration_log.id = migration_log_id

    return migration_log
