import datetime
import os
import time

from swarm.scraper.auth import Settings
import humanize

from django.conf import settings

from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Session, InstagramAccount, Media, InstagramLoginAccount, State
from django.contrib import messages
from django.utils import timezone

import logging
from random import randint
from time import sleep
from django.utils.translation import ngettext

logger = logging.getLogger(__name__)

class SessionAdmin(admin.ModelAdmin):
    pass
    list_display = ('first_name', 'status')

class InstagramAccountAdmin(admin.ModelAdmin):
    pass
    list_display = ('handle', 'status', 'session')

class MediaAdmin(admin.ModelAdmin):
    pass
    list_display = ('media_id', 'media_type', 'account')


class InstagramLoginAccountAdmin(admin.ModelAdmin):
    actions = ['reenable_accounts', 'disable_accounts', 'test_accounts_s', 'test_accounts_m', 'test_accounts_l']
    list_display = ('username', 'password', 'error_count', 'disabled')

    def disabled(self, obj: InstagramLoginAccount):
        if not obj.dont_use_until:
            return ''

        time_delta = obj.dont_use_until - timezone.now()

        if time_delta < datetime.timedelta(0):
            return ''

        if time_delta > datetime.timedelta(weeks=10*52):
            return 'Permanently'

        return humanize.naturaldelta(time_delta)

    def save_model(self, request, obj, form, change):
        handle = form.cleaned_data.get('username')
        file_path = f'instagrapi/{handle}.json'
        if not change and not os.path.isfile(file_path):
            logger.info(f'Creating new instagrapi settings file for new instagram login account {handle}')
            f = open(file_path, 'w')
            f.write(Settings().to_json())
            f.close()

        super().save_model(request, obj, form, change)


    @admin.action(description='Disable selected accounts')
    def disable_accounts(self, request, queryset):
        updated = queryset.update(dont_use_until=timezone.now() + settings.DISABLED_INSTAGRAM_TIMEOUT_PERM)
        self.message_user(request, ngettext(
            '%d account was successfully disabled.',
            '%d accounts were successfully disabled.',
            updated,
        ) % updated, messages.SUCCESS)


    @admin.action(description='Re-enable selected accounts')
    def reenable_accounts(self, request, queryset):
        updated = queryset.update(dont_use_until=None, error_count=0)
        self.message_user(request, ngettext(
            '%d account was successfully re-enabled.',
            '%d accounts were successfully re-enabled.',
            updated,
        ) % updated, messages.SUCCESS)


    @admin.action(description='Test selected accounts (small sleep)')
    def test_accounts_s(self, request, queryset):
        self.test_accounts_impl(request, queryset, 'SHORT')


    @admin.action(description='Test selected accounts (30-45 second sleep)')
    def test_accounts_m(self, request, queryset):
        self.test_accounts_impl(request, queryset, 'MEDIUM')


    @admin.action(description='Test selected accounts (3-5 minute sleep)')
    def test_accounts_l(self, request, queryset):
        self.test_accounts_impl(request, queryset, 'LONG')


    def test_accounts_impl(self, request, queryset, delay):
        msg = ''
        ok = 0
        for i, login_account in enumerate(queryset):
            if i > 0:
                if delay == 'SHORT':
                    dur = randint(5, 10)
                elif delay == 'MEDIUM':
                    dur = randint(30, 45)
                else:
                    dur = randint(180, 300)

                logger.info(f'Sleeping {dur} seconds...')
                sleep(dur)

            from .tasks import test_account
            res = test_account(login_account)

            if res:
                msg += f'{login_account.username}: OK. '
                ok += 1
            else:
                msg += f'{login_account.username}: ERROR. '

        status = messages.WARNING
        if ok == len(queryset):
            status = messages.SUCCESS
        elif ok == 0:
            status = messages.ERROR

        self.message_user(request, msg, status)

class StateAdmin(admin.ModelAdmin):
    pass
    list_display = ('__str__',)

admin.site.site_header = 'SCRAPE_ELEGY Administration'
admin.site.site_title = 'SCRAPE_ELEGY'

admin.site.register(InstagramAccount, InstagramAccountAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(Media, MediaAdmin)
admin.site.register(InstagramLoginAccount, InstagramLoginAccountAdmin)
admin.site.register(State, StateAdmin)

