import datetime
import os
import traceback
import uuid
from django.conf import settings
import time
from math import ceil
import random
import numpy as np

from random import randint
from django.core.mail import mail_admins
from django.utils import timezone
import instagrapi
from huey import crontab
from huey.contrib.djhuey import db_periodic_task, db_task, task, enqueue, lock_task
import http.client as httplib

import huey.contrib.djhuey as huey
from huey.exceptions import TaskException

from .swarm_client import SwarmClient
from setuptools.command.install import install

from . import utils
from .models import Session, State, ScrapeException
from .scraper.utils import get_snippet

from instagrapi import Client
from instagrapi.exceptions import ClientError, ClientThrottledError, UserNotFound, BadPassword
from django.utils.text import slugify
from .scraper.timer import Timer
from .scraper.colors import Colors, colorify
from .speech_synthesis import synthesise

from .models import Media, InstagramLoginAccount, InstagramAccount

import channels
from asgiref.sync import async_to_sync

from channels.generic.websocket import WebsocketConsumer
from .audio_journey import *
import logging

SCRAPE_PAGINATION_AMOUNT = 50

# If you have more than MAX_SCRAPE_HIGH posts, we will scrape up to MAX_SCRAPE_LOW posts
# If you have less than MAX_SCRAPE_HIGH posts, we will scrape all your posts
MAX_SCRAPE_LOW  = 200
MAX_SCRAPE_HIGH = 350

# Begin - parameters for media selection algorithm
CHAR_TARGET_LOW = 75
CHAR_TARGET_HIGH = 150
CHAR_TARGET_MID = (CHAR_TARGET_LOW + CHAR_TARGET_HIGH) / 2
CHAR_TARGET_FALLOFF = 50

TIMEOUT = 120 * 10 ** 9
PROCESSING_TIMEOUT = 45 * 10 ** 9
FOLLOW_TIMEOUT_X = 300 * 10 ** 9

TIME_TARGET = datetime.timedelta(minutes=4, seconds=46)
TIME_BG     = datetime.timedelta(minutes=4, seconds=52) # Duration of the background audio
TIME_FAKE   = datetime.timedelta(minutes=5, seconds=5)  # Duration of the fake audio, but I reduced by 7 seconds.

# This is a rough estimate of the duration of a single media, INCLUDING THE PAUSE AFTER IT
# TODO: (that will never happen - not enough time) don't rely on this, actually count words and approximate
#  or look at past snippets and time spent and approximate using that.
APPROX_MEDIA_DURATION = datetime.timedelta(seconds=7.5)

MAX_FOLLOW_ATTEMPTS = 2

logger = logging.getLogger(__name__)

channel_layer = channels.layers.get_channel_layer()


class NoAvailableInstagramLoginAccountsException(Exception):
    pass


class ChallengeRequiredException(Exception):
    pass


class NoInternetException(Exception):
    pass


def have_internet():
    conn = httplib.HTTPSConnection("8.8.8.8", timeout=5)
    try:
        conn.request("HEAD", "/")
        return True
    except Exception:
        return False
    finally:
        conn.close()


def assign_account_weight(i):
	if i == 0:
		return 15
	elif i == 1:
		return 5
	elif i == 2:
		return 3
	else:
		return 1


def recommission_account(login_account):
	login_account.error_count = 0
	login_account.dont_use_until = None
	login_account.last_used = timezone.now()
	login_account.save()


def decommission_account(login_account, duration = 'DEFAULT'):

	timeout = settings.DISABLED_INSTAGRAM_TIMEOUT
	if duration == 'LONG':
		timeout = settings.DISABLED_INSTAGRAM_TIMEOUT_LONG
	elif duration == 'PERM':
		timeout = settings.DISABLED_INSTAGRAM_TIMEOUT_PERM

	login_account.dont_use_until = timezone.now() + timeout
	login_account.error_count = login_account.error_count + 1
	login_account.save()


def challenge_code_give_up_handler(username, choice):
	logger.critical("challenge_code_give_up_handler executing to give up")
	raise ChallengeRequiredException


def change_password_handler(username):
	chars = list("abcdefghijklmnopqrstuvwxyzABCEDFGHIJKLMNOPQRSTUVWXYZ1234567890!&£@#")
	password = "".join(random.sample(chars, 16))

	msg = f"change_password_handler executing. Attempting to change password of {username} to {password}"
	logger.critical(msg)

	f = open("instagrapi/password_changes.txt", "a")
	f.write(msg)
	f.close()

	return password


def scrape_instagram_init(handle):

	# Fetch the login accounts, ignoring all that are set as don't use
	login_accounts = InstagramLoginAccount.objects.exclude(dont_use_until__gte=timezone.now()).order_by('last_used')

	# If no valid accounts
	if not len(login_accounts):
		raise NoAvailableInstagramLoginAccountsException

	# Sort the accounts, weighted
	weights = [assign_account_weight(i) for i in range(len(login_accounts))]
	weights = [x / sum(weights) for x in weights]
	login_accounts = list(np.random.choice(login_accounts, size=len(login_accounts), replace=False, p=weights))
	login_ok = False
	logger.info(f'login_accounts: {str(login_accounts)}')

	while len(login_accounts):

		login_account = login_accounts.pop(0)
		login_account.last_used = timezone.now()
		login_account.save()

		try:
			return scrape_instagram_init_with_account(handle, login_account)

		except UserNotFound as e:
			# This is an error we expect. Re-raise to handle in outer function
			logger.info("User not found")
			raise e

		except ChallengeRequiredException as e:
			logger.critical(f'LOGIN WITH ACCOUNT {login_account.username} FAILED BECAUSE IT REQUIRED A CHALLENGE.')
			logger.exception(e)
			decommission_account(login_account, 'LONG')

			# If we haven't managed to login and there are no more accounts to try, give up
			if not len(login_accounts):
				logger.critical('Raising NoAvailableInstagramLoginAccountsException')
				raise NoAvailableInstagramLoginAccountsException()

		except BadPassword as e:
			logger.critical(f'LOGIN WITH ACCOUNT {login_account.username} FAILED BECAUSE OF BAD PASSWORD.')
			logger.exception(e)
			decommission_account(login_account, 'LONG')

			# If we haven't managed to login and there are no more accounts to try, give up
			if not len(login_accounts):
				logger.critical('Raising NoAvailableInstagramLoginAccountsException')
				raise NoAvailableInstagramLoginAccountsException()

		except ClientError as e:
			# Something mysterious went wrong. If we otherwise have access to the internet, we have to assume
			# this account is decommissioned, hopefully temporarily
			logger.critical(f'LOGIN WITH ACCOUNT {login_account.username} FAILED.')
			logger.exception(e)

			if have_internet():
				logger.critical('WE HAVE INTERNET. Decommissioning account')
				decommission_account(login_account)
			else:
				logger.critical('It appears we don\'t have an internet connection...')
				raise NoInternetException()

			# If we haven't managed to login and there are no more accounts to try, give up
			if not len(login_accounts):
				logger.critical('Raising NoAvailableInstagramLoginAccountsException')
				raise NoAvailableInstagramLoginAccountsException()

		except Exception as e:
			# Something even more mysterious went wrong. If we otherwise have access to the internet, we have to assume
			# this account is decommissioned, hopefully temporarily
			logger.critical(f'LOGIN WITH ACCOUNT {login_account.username} FAILED BECAUSE OF ???')
			logger.exception(e)

			if have_internet():
				logger.critical('WE HAVE INTERNET. Decomissioning account')
				decommission_account(login_account, 'LONG')
			else:
				logger.critical('It appears we don\'t have an internet connection...')
				raise NoInternetException()

			# If we haven't managed to login and there are no more accounts to try, give up
			if not len(login_accounts):
				logger.critical('Raising NoAvailableInstagramLoginAccountsException')
				raise NoAvailableInstagramLoginAccountsException()


def scrape_instagram_init_with_account(handle, login_account, force_relogin=False):
	t = Timer()
	cl = SwarmClient()

	# If we are in prod mode, replace the challenge code handler with one that explodes when it's called
	# This is because the default handler hangs indefinitely
	# Also, replace the password change handler with one that generates a random password
	if not settings.DEBUG:
		cl.challenge_code_handler = challenge_code_give_up_handler
		cl.change_password_handler = change_password_handler

	t.start(f'Logging in as {login_account.username}')
	if os.path.isfile(f'instagrapi/{login_account.username}.json'):
		cl.load_settings(f'instagrapi/{login_account.username}.json')

	relogin = login_account.error_count >= settings.ERRORS_BEFORE_RELOGIN or force_relogin
	cl.try_login(login_account.username, login_account.password, relogin)

	t.stop()

	t.start('Getting User Info')
	user_info = cl.user_info_by_username(handle).dict()
	t.stop()

	recommission_account(login_account)

	return cl, user_info, login_account


def clamp(n, minn, maxn):
	return max(min(maxn, n), minn)


def scale(val, target, falloff):
	return 1 - min(abs(val - target) / falloff, 1)


def assign_weight(media, i, l, char_target):

	# Not exactly zero - just to handle the situation where all our medias are of length 0
	weight = 0.000001
	if not len(media.caption_text):
		return weight

	weight += scale(i + 0.5, l / 2, l / 2) * 10  # Scale from 0 to 10 based on distance from centre
	weight += scale(len(media.caption_text), char_target, CHAR_TARGET_FALLOFF) * 15  # Scale from 0 to 15 based on char target

	return weight


def choose_media_in_bucket(medias, idx_from, idx_to, char_target) -> int:

	medias_to_consider = medias[idx_from:idx_to]
	weights = [assign_weight(media, i, len(medias_to_consider), char_target) for i, media in enumerate(medias_to_consider)]

	# Take the most representative media from the sample, within reason.
	# Really try not to take medias with no caption.
	# chosen_media = min(medias_to_consider, key=lambda media: abs(len(media.caption_text) - char_target) + (1000 if len(media.caption_text) == 0 else 0))
	chosen_media = random.choices(medias_to_consider, weights=weights)[0]
	idx = list(medias).index(chosen_media)

	return idx




@task()
def reset_state():
	utils.update_state(1)



@db_task()
def scrape_instagram(instagram_account_id, session, handle):
	logger.info("scrape_instagram")

	t_global = Timer()
	t_global.start("Entire script", False)

	utils.send_frontend_message({
		'type': 'LOAD'
	})

	utils.send_audio_message({
		'type': 'LOAD'
	})

	# Start the instagram task. This will run as a second task in the background, and save stuff to the DB
	# We query the DB to get medias, later
	complete = False
	finalised = False

	# Tracking the duration / number of audios
	curr_time = datetime.timedelta()
	curr_count = 0
	prev_idx = -1
	prev_idx_to = None

	intermissions = get_intermissions()
	effects = get_effects()
	effect = None

	# Note use of hyphen, so it's not a valid instagram handle
	fake = handle == 'FAKE-RUN' or handle == 'FAKE-AUDIO'

	if fake:
		medias = [Media(caption_text=x) for x in get_fake_posts()]
		logger.info(medias)
		complete = True
		utils.update_state(2)
	else:
		scrape_task = scrape_instagram_impl(handle, instagram_account_id, session)
		medias = []

	t_start = time.time_ns()

	logger.info(colorify('Waiting stage one', Colors.CYAN))

	# Wait to confirm
	while utils.is_session_preprocessing(session.pk):

		if (time.time_ns() - t_start) > PROCESSING_TIMEOUT:
			logger.critical("TIMEOUT from Huey Task")
			utils.send_frontend_message({
				'type': 'ERROR',
				'error': 'INSTAGRAM_BLOCKED_US'
			})
			utils.update_state(1)
			session.status = 7 # Bit of a lie but w/e
			session.save()
			return
		else:
			time.sleep(1.5)
			continue

	logger.info(colorify('Waiting stage two', Colors.CYAN))

	# Wait to confirm that the task has moved on from processing
	while utils.is_processing():

		if (time.time_ns() - t_start) > FOLLOW_TIMEOUT_X:
			logger.critical("TIMEOUT from Huey Task at following stage")
			utils.send_frontend_message({
				'type': 'ERROR',
				'error': 'INSTAGRAM_BLOCKED_US'
			})
			utils.update_state(1)
			session.status = 7 # Bit of a lie but w/e
			session.save()
			return
		else:
			time.sleep(1.5)
			continue

	logger.info(colorify('Waiting stages completed', Colors.CYAN))

	# Check if cancelled via the magic of triple tap
	session = Session.objects.get(pk=session.pk)
	if session.status == 7:
		logger.info('User interrupt processed')
		return

	# Cleanly exit here if state was set to ready - it should be occupied instead
	if utils.is_ready():
		return

	time.sleep(settings.DELAY_START.total_seconds())

	# We can get away with this because we always have one intermission right at the start, sent immediately
	start_time = timezone.now()

	# Play the waiting game
	while not finalised:

		# Check if cancelled via the magic of triple tap
		session = Session.objects.get(pk=session.pk)
		if session.status == 7:
			logger.info('User interrupt processed')
			return

		# Check to see if something went terribly wrong in the scrape_task...
		if not fake:
			try:
				res = scrape_task()

				if res == 'SCRAPE_ERROR':
					logger.critical("UHOH, our Huey task has failed")
					break

			except TaskException as e:
				logger.critical("UHOH, our Huey task has failed")
				break

		# Play any required intermissions
		if intermissions and intermissions[0].timestamp <= curr_time:
			intermission = intermissions.pop(0)

			if intermission.type == IntermissionType.STATIC_AUDIO:
				transmit_audio(intermission.audio_file, '', intermission.effect)
				curr_time += intermission.duration
				if not complete:
					time.sleep(intermission.duration.total_seconds() * 0.9)

			elif intermission.type == IntermissionType.PAUSE:
				transmit_pause(intermission.duration)
				curr_time += intermission.duration
				if not complete:
					time.sleep(intermission.duration.total_seconds() * 0.9) # Sleep a touch less

			elif intermission.type == IntermissionType.BACKGROUND_AUDIO:
				# Don't sleep or add to currtime
				transmit_audio(intermission.audio_file, '', intermission.effect, True)

			elif intermission.type == IntermissionType.REPEAT_LAST:
				media = medias[prev_idx]
				synth_result = synthesise_media(media, handle, intermission.effect)

				# TODO: Consider handling this with exceptions
				if synth_result['audio_duration']:
					transmit_audio(synth_result['file_name'], synth_result['caption'], intermission.effect)
					curr_time += synth_result['audio_duration'] + intermission.effect.gap
				else:
					logger.warning('Failed to synthesise media. Trying to continue anyway...')

				# This allows us to catch up to the still-downloading medias when we're not complete
				if not complete:
					time.sleep(max(0, synth_result['audio_duration'].total_seconds() - 1.5))

			elif intermission.type == IntermissionType.PLAY_INSTAGRAM_HANDLE:
				snippet = f'{handle}, {handle}, {handle}'
				file_name = f'{slugify(handle)}-{handle}-{str(uuid.uuid4().hex)}.mp3'
				audio_duration = synthesise(snippet, file_name, intermission.effect)

				# TODO: Consider handling this with exceptions
				if audio_duration:
					transmit_audio(f'/static/audio/{file_name}', '', intermission.effect)
					curr_time += audio_duration + intermission.effect.gap
				else:
					logger.warning('Failed to synthesise media. Trying to continue anyway...')

				# This allows us to catch up to the still-downloading medias when we're not complete
				if not complete:
					time.sleep(max(0, audio_duration.total_seconds() - 1.5))

			# Get out if there's no intermissions left, because our final intermissions ends the experience
			if not len(intermissions):
				break

			continue

		if not complete:
			complete = InstagramAccount.objects.get(id=instagram_account_id).status == 2
			medias = Media.objects.filter(account_id=instagram_account_id)

			if len(medias) < 50 and not complete:
				logger.info("Waiting...")

				if (time.time_ns() - t_start) > TIMEOUT:
					logger.critical("TIMEOUT")
					complete = True
				else:
					time.sleep(1.5)
					continue

		if not len(medias):
			logger.critical('This instagram user appears to have no posts')
			return

		idx = -1

		# Determine effect. Every effect is guaranteed to be used at least once (unless we run out of time)
		if effects and effects[0].timestamp <= curr_time:
			effect = effects.pop(0)

		time_remaining = TIME_TARGET - curr_time

		logger.debug(f'time_remaining {time_remaining}')

		# Now, choose the next media!
		# If this is the first media we're choosing - just choose the first one
		if curr_count == 0:
			idx = 0

		# If we're getting real close to the end - choose the final media that has a caption and be done with it
		elif time_remaining < APPROX_MEDIA_DURATION:
			finalised = True
			found_one = False
			for i in reversed(range(prev_idx + 1, len(medias))):
				if len(medias[i].caption_text):
					idx = i
					found_one = True
					break

			if not found_one:
				break

		# If complete and we already chose the last media - exit
		elif complete and prev_idx == (len(medias) - 1):
			logger.info('Reached end of medias')
			break

		# If complete and we haven't already chosen the last media:
		elif complete:

			# Calculate the average word count of the remaining medias
			idx_from = prev_idx + 1
			if prev_idx_to and (len(medias) - prev_idx_to) > 10:
				idx_from = prev_idx_to # Since this number was exclusive, we don't need to + 1

			remaining_medias = medias[idx_from:]

			avg_chars = sum([len(media.caption_text) for media in remaining_medias]) / len(remaining_medias)
			# avg_duration = datetime.timedelta(seconds=avg_words/APPROX_SPEAKING_RATE)

			char_target = clamp(avg_chars, CHAR_TARGET_LOW, CHAR_TARGET_HIGH)
			logger.debug(f'avg_chars {avg_chars}, char_target {char_target}')

			idxs_available = len(medias) - idx_from - 1
			approx_medias_left = time_remaining / APPROX_MEDIA_DURATION
			bucket_size = max(ceil(idxs_available / approx_medias_left), 1)

			idx_to = idx_from + bucket_size  # Exclusive

			if idx_to > len(medias):
				logger.warning('Generated out of bounds bucket size. Probably reached end of medias. Terminating')
				break

			logger.debug(f'bucket size: {idxs_available / approx_medias_left}')

			idx = choose_media_in_bucket(medias, idx_from, idx_to, char_target)

			prev_idx_to = idx_to

		# If not complete and there's not many medias to choose from - just wait a bit
		elif (len(medias) - prev_idx) <= 10:
			logger.info('Pausing for more medias')
			time.sleep(1.5)
			continue

		else:
			# Choose posts at indices approximately push % of the way 'down', that is, from the index of the previous post to the last index available
			# push starts at 10% but quickly ramps to 25% at 30 seconds in
			# bucket_radius starts at 3 (look +- 3 away from the centered index - 7 total) but climbs to 6 (size 13 total)

			progress = 1 - scale(curr_time.total_seconds(), 0, 30) # 0 at the the start, 1 30 seconds in and later
			push = 0.1 + progress * 0.15
			bucket_radius = 3 + progress * 3

			idxs_available = len(medias) - prev_idx - 1
			center_index = idxs_available * push + prev_idx + 0.5

			idx_from = max(round(center_index - bucket_radius), prev_idx + 1)
			idx_to = min(round(center_index + bucket_radius + 1), len(medias) - 1)

			logger.debug(f'push: {push}, idxs_available: {idxs_available}, center_index: {center_index}, idx_from: {idx_from}, : {idx_to}')

			idx = choose_media_in_bucket(medias, idx_from, idx_to, CHAR_TARGET_MID)

		logger.debug(f'Chosen idx: {idx}')

		chosen_media = medias[idx]
		logger.debug(chosen_media)

		if complete and idx == (len(medias) - 1):
			finalised = True

		if len(chosen_media.caption_text):

			# We do this synchronously - one request to Azure at a time
			synth_result = synthesise_media(chosen_media, handle, effect)

			# TODO: Consider handling this with exceptions
			if synth_result['audio_duration']:
				transmit_audio(synth_result['file_name'], synth_result['caption'], effect)
				curr_time += synth_result['audio_duration'] + effect.gap
				chosen_media.audio_filename = synth_result['file_name']
				if not fake:
					chosen_media.save()
			else:
				logger.warning('Failed to synthesise media. Trying to continue anyway...')

			# This allows us to catch up to the still-downloading medias when we're not complete
			if not complete:
				time.sleep(max(0, synth_result['audio_duration'].total_seconds() - 0.5))

		else:
			logger.info('Chosen media has no caption. Skipping')

		curr_count += 1
		prev_idx = idx

	# If there exists more intermissions - forcibly play the final one if it is a static_audio
	if intermissions:
		intermission = intermissions.pop()

		if intermission.type == IntermissionType.STATIC_AUDIO:
			transmit_audio(intermission.audio_file, '', intermission.effect)
			curr_time += intermission.duration
			time.sleep(intermission.duration.total_seconds())

	eta = start_time + settings.DELAY_END + max(curr_time, TIME_BG)

	# Check if cancelled via the magic of triple tap
	session = Session.objects.get(pk=session.pk)
	if session.status == 7:
		logger.info('User interrupt processed')
		return

	# Only consider setting an ETA if we successfully scraped at least something. Otherwise, just set state back to ready
	if len(medias) and eta > timezone.now():
		utils.update_audiostream_end_eta(eta)
		logger.info("Updated audiostream end eta to " + str(eta - timezone.now()) + " from now")
	else:
		utils.update_state(1)

	# Done!
	t_global.stop()












@db_task()
def scrape_instagram_dummy():
	logger.info("scrape_instagram_dummy")

	utils.send_frontend_message({
		'type': 'LOAD'
	})

	utils.send_audio_message({
		'type': 'LOAD'
	})

	eta = timezone.now() + settings.DELAY_START + TIME_FAKE + settings.DELAY_END
	utils.update_audiostream_end_eta(eta, True) # Bit obscure, but this also sets the state to 2, occupied, and sends message including dummy mention

	time.sleep(settings.DELAY_START.total_seconds())
	transmit_audio('/static/audio_samples/FAKE_AUDIO.mp3', 'Example audio', Effect())




def mark_account_complete(instagram_account_id, session):
	instagram_account = InstagramAccount.objects.get(pk=instagram_account_id)
	instagram_account.status = 2  # Complete
	instagram_account.save()

	session.status = 4  # Presenting
	session.save()


# SPEAKING_RATE = 3.0  # (Words / seconds)
# TARGET_WORDS = TIME_TARGET.total_seconds() * SPEAKING_RATE

# Should add to 1. This is the target portion of the total words for each scraping step
TARGET_PORTION_PER_STEP = [0.12, 0.24, 0.64]


def synthesise_media(media: Media, handle: str, effect: Effect):
	t = Timer()
	t.start('Synthesising audio')

	snippet = get_snippet(media.caption_text)
	file_name = slugify(handle) + '-' + str(uuid.uuid4().hex) + '.mp3'
	logger.info(f'Caption: {snippet}')
	audio_duration = synthesise(snippet, file_name, effect)

	t.stop()

	return {
		'audio_duration': audio_duration,
		'file_name': f'/static/audio/{file_name}',
		'caption': (str(media.date_media.date()) + ' - ' if media.date_media else '') + snippet
	}

def transmit_pause(duration: dt.timedelta):
	utils.send_audio_message({
		'type': 'PAUSE',
		'text': 'Waiting...',
		'duration': round(duration.total_seconds() * 1000),
	})

def transmit_audio(file_name, caption, effect: Effect, background=False):
	utils.send_audio_message({
		'type': 'AUDIO',
		'background': background,
		'index': 0,
		'url': file_name,
		'text': caption,
		'gap': round(effect.gap.total_seconds() * 1000),
		'volume': effect.volume
	})


def test_account(login_account: InstagramLoginAccount):
	logger.info(f'Testing account {login_account.username}')

	try:
		handle = 'instagram'
		cl, user_info, login_account = scrape_instagram_init_with_account(handle, login_account, True)
		medias, end_cursor = cl.user_medias_paginated(user_info['pk'], 10)
	except Exception as e:
		logger.warning(f'Acccount tested. Outcome: ERROR')
		logger.exception(e)
		decommission_account(login_account, 'PERM')
		return False

	logger.info(f'Acccount tested. Outcome: OK')
	recommission_account(login_account)

	return True


@db_task()
def scrape_instagram_impl(handle: str, instagram_account_id: str, session: Session):

	medias = []

	try:
		cl = None
		user_info = None

		try:
			cl, user_info, login_account = scrape_instagram_init(handle)

			# Check if cancelled via the magic of triple tap
			session = Session.objects.get(pk=session.pk)
			if session.status == 7:
				logger.info('User interrupt processed')
				return

		except NoInternetException:
			logger.critical('We don\'t have internet')
			utils.send_frontend_message({
				'type': 'ERROR',
				'error': 'NO_INTERNET'
			})
			return 'SCRAPE_ERROR'

		except NoAvailableInstagramLoginAccountsException:
			logger.critical('We don\'t have any valid instagram login accounts')
			utils.send_frontend_message({
				'type': 'ERROR',
				'error': 'INSTAGRAM_BLOCKED_US'
			})
			return 'SCRAPE_ERROR'

		except UserNotFound:
			utils.send_frontend_message({
				'type': 'ERROR',
				'error': 'USER_DOES_NOT_EXIST',
				'handle': handle
			})
			return 'SCRAPE_ERROR'

		except Exception as e:
			logger.critical('Unknown error - Instagram may have blocked us')
			logger.exception(e)
			utils.send_frontend_message({
				'type': 'ERROR',
				'error': 'GENERIC'
			})
			return 'SCRAPE_ERROR'

		if user_info['media_count'] == 0:
			utils.send_frontend_message({
				'type': 'ERROR',
				'error': 'USER_NO_MEDIAS',
				'handle': handle
			})
			return 'SCRAPE_ERROR'

		follow_attempts = 0
		state_updated = False

		if settings.NOTIFY_EARLY and 'is_private' in user_info and not user_info['is_private']:
			state_updated = True
			utils.update_state(2)	# This signals to the other thread to start things
			session.status = 3
			session.save()

		user_id = user_info['pk']

		logger.info(f'User Info: {user_info}')

		t = Timer()
		t.start('Getting medias')

		end_cursor = ''
		max_scrape = MAX_SCRAPE_HIGH if (user_info['media_count'] <= MAX_SCRAPE_HIGH) else MAX_SCRAPE_LOW

		try:
			while len(medias) < max_scrape:

				# Check if cancelled via the magic of triple tap
				session = Session.objects.get(pk=session.pk)
				if session.status == 7:
					logger.info('CANCELLED - EXITING')
					return 'USER_INTERRUPTED'

				new_medias, end_cursor = cl.user_medias_paginated(user_id, SCRAPE_PAGINATION_AMOUNT, end_cursor)

				if len(new_medias):

					if not state_updated:
						state_updated = True
						utils.update_state(2)	# This signals to the other thread to start things
						session.status = 3
						session.save()

					# Convert these to nice database objects. The constructor handles media dict -> Media obj
					new_medias = [Media.create_from_igrapi(instagram_account_id, media) for media in new_medias]

					# Write ALL these medias to the DB, immediately, then add them to our medias list
					Media.objects.bulk_create(new_medias)
					medias.extend(new_medias)

					logger.info(f'Total loaded: {len(medias)}')
					dur = randint(5, 20)
					logger.info(f'Sleeping {dur} seconds...')
					time.sleep(dur)

				else:

					if len(medias):
						logger.info("Reached end of medias")
						break

					else:
						# This means we have an account, it ought to have medias, but we can't read any
						if 'is_private' in user_info and not user_info['is_private']:
							logger.critical("Unexpected error")
							# The account is public but we still don't have access? Ok, something is broken
							# I don't anticipate this should happen
							utils.send_frontend_message({
								'type': 'ERROR',
								'error': 'INSTAGRAM_BLOCKED_US'
							})
							return 'SCRAPE_ERROR'

						# Conclusion -> account is private and we don't have access
						end_cursor = ''

						session.status = 2
						session.save()

						if follow_attempts < MAX_FOLLOW_ATTEMPTS:
							follow_attempts += 1

							logger.info("SENDING FOLLOW REQUEST")

							try:
								cl.user_follow(user_id)
							except Exception as e:
								logger.critical("Error when sending follow request")
								logger.exception(e)
								decommission_account(login_account)
								utils.send_frontend_message({
									'type': 'ERROR',
									'error': 'INSTAGRAM_BLOCKED_US'
								})
								return 'SCRAPE_ERROR'

							utils.send_frontend_message({
								'type': 'ERROR',
								'error': 'NEED_FOLLOW',
								'attempt': follow_attempts,
								'attemptsMax': MAX_FOLLOW_ATTEMPTS,
								'handle': handle,
								'fromHandle': login_account.username
							})

							# Wait for status to change, or up to 2 minutes
							t_start = time.time_ns()

							def is_session_waiting_for_follow():
								nonlocal session
								session = Session.objects.get(pk=session.pk)
								return session.status == 2

							while is_session_waiting_for_follow():

								if (time.time_ns() - t_start) > TIMEOUT:
									logger.critical("Wait for follow - TIMEOUT")

									utils.send_frontend_message({
										'type': 'ERROR',
										'error': 'NEED_FOLLOW_FINAL'
									})
									return 'SCRAPE_ERROR'

								else:
									logger.info("Wait for follow resp")
									time.sleep(1.5)
									continue

							# Check if user declined follow request
							session = Session.objects.get(pk=session.pk)
							if session.status == 6:
								return 'SCRAPE_ERROR'

						else:
							utils.send_frontend_message({
								'type': 'ERROR',
								'error': 'NEED_FOLLOW_FINAL'
							})
							return 'SCRAPE_ERROR'

				if len(medias) and not end_cursor:
					logger.info("Reached end of medias")
					break

		except ClientError as e:
			logger.critical("Unexpected ClientError when scraping medias")
			decommission_account(login_account)

			if not len(medias):
				utils.send_frontend_message({
					'type': 'ERROR',
					'error': 'INSTAGRAM_BLOCKED_US'
				})
			logger.exception(e)

		except Exception as e:
			logger.critical("Unexpected error when scraping medias")

			if not len(medias):
				utils.send_frontend_message({
					'type': 'ERROR',
					'error': 'GENERIC'
				})
			logger.exception(e)

		t.stop()
		logger.info(colorify(f"Loaded {len(medias)} medias!", Colors.GREEN_BOLD))

		# Check if cancelled via the magic of triple tap
		session = Session.objects.get(pk=session.pk)
		if session.status == 7:
			logger.info('User interrupt processed')
			return 'USER_INTERRUPTED'

		# Update the status of the instagram account and session
		mark_account_complete(instagram_account_id, session)

	finally:

		# If something went terribly wrong and we weren't able to get even a single media - GTFO
		if not len(medias):
			utils.update_state(1)
			session.status = 6
			session.save()
			return 'SCRAPE_ERROR'


