import logging
from django.core.mail import mail_admins
from huey.contrib.djhuey import task

logger = logging.getLogger(__name__)

class EmailHandler(logging.Handler):
    def emit(self, record):
        mail_admin_task(record)

@task()
def mail_admin_task(record):
    logger.info("Notifying admins")
    mail_admins("Error with SCRAPE_ELEGY application", record.getMessage())


# Huey doesn't support scheduling tasks, just locking them and failing if lock couldn't be acquired (...)
#
# from huey.exceptions import TaskLockedException
#  ...
# try:
#     mail_admin_task(record)
# except TaskLockedException:
#     logger.warning("Couldn't send email because task is locked")
#  ...
# @task(retries=3, retry_delay=10)
# @lock_task('mail-admin-task-lock')
