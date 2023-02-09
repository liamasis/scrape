# chat/consumers.py
import datetime
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer, JsonWebsocketConsumer

from django.conf import settings

import logging

from swarm import utils
from swarm.models import State

logger = logging.getLogger(__name__)

class FrontendStreamConsumer(JsonWebsocketConsumer):

    # All FrontendStreamConsumer will belong to the same group
    room_group_name = settings.HOME_ROOM_GROUP_NAME

    def connect(self):
        logger.info("New Frontend Connection")

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

        from .utils import create_state_change_message
        self.send_json(create_state_change_message())

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive_json(self, content):

        if content['type'] == 'FOLLOW_RESP_OK':
            logger.info("Received follow resp ok message")
            state = State.objects.get(pk=1)
            session = state.active_session
            if session:
                session.status = 1
                session.save()

        elif content['type'] == 'FOLLOW_RESP_DECLINED':
            logger.warning("Received follow resp declined message")
            state = State.objects.get(pk=1)
            session = state.active_session
            if session:
                session.status = 6
                session.save()

        elif content['type'] == 'USER_INTERRUPT':
            logger.warning("Received interrupt message")
            state = State.objects.get(pk=1)
            session = state.active_session
            if session:
                session.status = 7
                session.save()
                utils.update_state(1)

                utils.send_audio_message({
                    'type': 'USER_INTERRUPT'
                })

    # Receive message from room group
    def frontend_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send_json(message)





class AudioStreamConsumer(JsonWebsocketConsumer):

    # All AudioStreamConsumers will belong to the same group
    room_group_name = settings.AUDIO_ROOM_GROUP_NAME

    def connect(self):
        logger.info("New Audio Connection")

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

        message = {
            'type': 'AUDIO',
            'index': 0,
            'url': f'/static/audio_samples/connected.mp3',
            'text': 'Connected to SCRAPE_ELEGY server. You should hear "connected".'
        }
        self.send_json(message)
        # self.send_json(message)
        # self.send(text_data=json.dumps(message, indent=None, separators=(',', ':')))

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive_json(self, content):
        pass

    # Receive message from room group
    def audio_message(self, event):
        message = event['message']

        # Send message to WebSocket
        # self.send(text_data=json.dumps(message, indent=None, separators=(',', ':')))
        self.send_json(message)
