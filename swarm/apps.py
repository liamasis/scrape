import datetime

from django.apps import AppConfig
from django.utils import timezone
import sys

import logging
logger = logging.getLogger(__name__)

class SwarmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'swarm'

    def ready(self):

        logger.info("💕 SCRAPE_ELEGY starting up... 💕")

        if 'runserver' not in sys.argv and 'daphne' not in sys.argv and '/usr/local/bin/daphne' not in sys.argv:
            logger.debug(f'Not resetting state because {sys.argv}')
            return

        from .models import State

        logger.debug('Resetting state')
        if State.objects.exists():
            s = State.objects.get(pk=1)
            s.state = 1
            s.date_ready = None
            s.save()
        else:
            s = State(state=1)
            s.save()
