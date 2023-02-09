import logging

from asgiref.sync import async_to_sync
import datetime
import math

from django.utils import timezone
from . import tasks

from django.conf import settings
import channels

from .models import State, Session

channel_layer = channels.layers.get_channel_layer()
logger = logging.getLogger(__name__)

def send_frontend_message(data):
	async_to_sync(channel_layer.group_send)(
		settings.HOME_ROOM_GROUP_NAME,
		{
			'type': 'frontend_message',
			'message': data
		}
	)

def send_audio_message(data):
	async_to_sync(channel_layer.group_send)(
		settings.AUDIO_ROOM_GROUP_NAME,
		{
			'type': 'audio_message',
			'message': data
		}
	)

# We shouldn't need to rely on the task most of the time - as the audiostream client should message us and tell us that it's done earlier
scheduled_state_reset_task = None

def update_audiostream_end_eta(eta, dummy=False):
	global scheduled_state_reset_task

	s = State.objects.get(pk=1)
	s.state = 2
	s.date_ready = eta
	s.save()

	if scheduled_state_reset_task:
		scheduled_state_reset_task.revoke()

	scheduled_state_reset_task = tasks.reset_state.schedule(eta=eta)

	send_frontend_message(create_state_change_message(2, eta, dummy))

def update_state(state):

	if state == 2:
		eta = timezone.now() + tasks.TIME_TARGET + settings.TIME_GUESS_BUFFER + settings.DELAY_START + settings.DELAY_END
		update_audiostream_end_eta(eta)
		return

	s = State.objects.get(pk=1)
	s.state = state
	s.date_ready = None
	s.save()

	send_frontend_message(create_state_change_message(state, None))


def update_state_and_session(session):

	state = 5

	s = State.objects.get(pk=1)
	s.state = state
	s.date_ready = None
	s.active_session = session
	s.save()

	send_frontend_message(create_state_change_message(state, None))

def create_state_change_message(state=None, eta=None, dummy=False):
	if not state:

		# Value error to provide state but not eta
		if eta:
			raise ValueError

		s = State.objects.get(pk=1)
		state = s.state
		eta = s.date_ready

	logger.debug(f'ETA is {eta}')

	return {
		'type': 'STATE_CHANGE',
		'state': state,
		'dummy': dummy if state == 2 else None,
		'eta': math.floor(eta.timestamp() * 1000) if state == 2 else None
	}

def is_ready():
	s = State.objects.get(pk=1)
	return s.state == 1

def is_occupied():
	s = State.objects.get(pk=1)
	return s.state == 2

def is_processing():
	s = State.objects.get(pk=1)
	return s.state == 5

def is_session_preprocessing(session_pk):
	s = State.objects.get(pk=1)
	session = Session.objects.get(pk=session_pk)
	return s.state == 5 and session.status == 1
