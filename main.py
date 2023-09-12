from datetime import datetime

import pytz
from fastapi import FastAPI
from fastapi_amis_admin.admin.settings import Settings
from fastapi_amis_admin.admin.site import AdminSite
from fastapi_scheduler import SchedulerAdmin

from common.startup.create_dummy_data import create_dummy_data

# Create `FastAPI` application
app = FastAPI()
# Create `AdminSite` instance
site = AdminSite(settings=Settings(database_url_async='sqlite+aiosqlite:///amisadmin.db'))
# Create an instance of the scheduled task scheduler `SchedulerAdmin`
scheduler = SchedulerAdmin.bind(site)


# Add scheduled tasks, refer to the official documentation: https://apscheduler.readthedocs.io/en/master/
# use when you want to run the job at fixed intervals of time
@scheduler.scheduled_job('interval', minute=5)
def interval_task_test():
    print(f'[{datetime.now()}] interval task is run...')


# use when you want to run the job periodically at certain time(s) of day
@scheduler.scheduled_job('cron', hour=2, minute=0, timezone=pytz.timezone('Asia/Seoul'))
def cron_task_test():
    print('cron task is run...')


@app.on_event("startup")
async def startup():
    # 데이터 동기화 예시를 위한 초기 데이터 세팅
    create_dummy_data()
    # Mount the background management system
    site.mount_app(app)
    # Start the scheduled task scheduler
    scheduler.start()
    print("scheduler start.")


@app.on_event("shutdown")
def shutdown_scheduler():
    scheduler.shutdown()
    print("scheduler shutdown gracefully.")


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app)
