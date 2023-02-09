import json
import logging
import time

from . import utils
from .models import State, InstagramLoginAccount

from django.http import HttpResponseBadRequest, HttpResponse

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie

from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.
from rest_framework import viewsets
from .serializers import MediaSerializer, InstagramAccountSerializer, SessionSerializer
from .models import Session, InstagramAccount, Media
from .tasks import scrape_instagram, scrape_instagram_dummy, scrape_instagram_init_with_account

from .scraper.utils import random_string
from .scraper.colors import Colors, colorify

logger = logging.getLogger(__name__)

# Create your views here.

class SessionView(viewsets.ModelViewSet):
    serializer_class = SessionSerializer
    queryset = Session.objects.all()

class InstagramAccountView(viewsets.ModelViewSet):
    serializer_class = InstagramAccountSerializer
    queryset = InstagramAccount.objects.all()

class MediaView(viewsets.ModelViewSet):
    serializer_class = MediaSerializer
    queryset = Media.objects.all()


#
# @ensure_csrf_cookie
# @api_view(['GET'])
# def get_csrf(request):
#     """
#     List all code snippets, or create a new snippet.
#     """
#     if request.method == 'GET':
#         return Response("CSRF")


# @api_view(['GET'])
# @csrf_exempt
# def account_reset(request):
#     if request.method == 'GET':
#
#         logger.info(colorify(f'API hit on ACCOUNT_RESET: {request.body}', Colors.YELLOW_BOLD))
#
#         try:
#             login_accounts = InstagramLoginAccount.objects.all()
#             login_accounts.update(dont_use_until=None, error_count=0)
#
#             return HttpResponse("OK", content_type="text/plain")
#
#         except Exception as e:
#             logger.exception(e)
#             return HttpResponse("Error", content_type="text/plain")
#
#
# @api_view(['GET'])
# @csrf_exempt
# def account_test(request):
#     if request.method == 'GET':
#
#         logger.info(colorify(f'API hit on ACCOUNT_TEST: {request.body}', Colors.YELLOW_BOLD))
#         msg = ''
#         login_accounts = InstagramLoginAccount.objects.all()
#
#         for login_account in login_accounts:
#
#             try:
#                 scrape_instagram_init_with_account('instagram', login_account, True)
#                 msg += f'{login_account.username}:\t\tOK' + '\r\n'
#
#             except Exception as e:
#                 logger.exception(e)
#                 msg += f'{login_account.username}:\t\tERROR' + '\r\n'
#
#         return HttpResponse(msg, content_type="text/plain")

@api_view(['POST'])
@csrf_exempt
def scrape(request):
    if request.method == 'POST':

        logger.info(colorify(f'API hit on SCRAPE: {request.body}', Colors.YELLOW_BOLD))

        if not utils.is_ready():
            return HttpResponseBadRequest("Audiostream is already running")

        data = json.loads(request.body.decode('utf-8'))

        if not data['instagramHandle']:
            return HttpResponseBadRequest("No handled provided")

        # s = Session(first_name=(data['firstName'] or random_string()))
        s = Session(first_name=(random_string()))
        i = InstagramAccount(handle=data['instagramHandle'], session=s)
        s.save()
        i.save()

        utils.update_state_and_session(s)

        scrape_instagram(i.id, s, data['instagramHandle'])

        return Response()




@api_view(['POST'])
@csrf_exempt
def scrape_dummy(request):
    if request.method == 'POST':
        
        logger.info(colorify(f'API hit on SCRAPE_DUMMY: {request.body}', Colors.YELLOW_BOLD))

        if not utils.is_ready():
            return HttpResponseBadRequest("Audiostream is already running")

        # s = Session(first_name=(data['firstName'] or random_string()))
        s = Session(first_name=('DUMMY_SCRAPE' + random_string()))
        s.save()

        utils.update_state_and_session(s)

        scrape_instagram_dummy()

        return Response()




