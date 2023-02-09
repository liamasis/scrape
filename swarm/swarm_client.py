import logging
from typing import List, Tuple

from instagrapi import Client
from instagrapi.exceptions import ReloginAttemptExceeded, ClientError, UserNotFound
from instagrapi.mixins.user import User
from instagrapi.types import Media

logger = logging.getLogger(__name__)


class SwarmClient(Client):

    def try_login(self, username: str, password: str, relogin: bool):

        if relogin:
            return self.try_relogin(username, password)

        login_ok = False
        try:
            login_ok = self.login(username, password)
        except Exception as e:
            logger.warning("Normal login failed with exception")
            logger.exception(e)
            login_ok = False

        if login_ok:
            self.dump_settings(f'instagrapi/{username}.json')
        else:
            logger.warning("Normal login failed")
            self.try_relogin(username, password)


    def try_relogin(self, username, password):
        relogin_ok = self.login(username, password, relogin=True) # This might throw an exception, which is intentional

        if relogin_ok:
            self.dump_settings(f'instagrapi/{username}.json')
        else:
            raise ClientError("Error during relogin")


    def handle_with_relogin(self, func, *args):
        """
        This will try to execute func. If it fails, it will relogin and try to execute func again
        :param func:
        :return: the result of func, or throws an exception
        """
        try:
            return func(*args)
        except UserNotFound as e:
            raise e
        except Exception as e:
            logger.warning(f'An error occured with an instagrapi call. Attempting relogin...')
            try:
                self.try_relogin(self.username, self.password)  # Note that on the second relogin attempt this will explode, which is what we want
                logger.warning(f'Relogin successful!')
                return func(*args)
            except Exception as e2:
                logger.exception(e)
                logger.exception(e2)
                raise e2


    def user_info_by_username(self, username: str, use_cache: bool = True) -> User:
        return self.handle_with_relogin(super(SwarmClient, self).user_info_by_username, username, use_cache)


    def user_medias_paginated(self, user_id: int, amount: int = 0, end_cursor: str = "") -> Tuple[List[Media], str]:
        return self.handle_with_relogin(super(SwarmClient, self).user_medias_paginated, user_id, amount, end_cursor)


    def user_follow(self, user_id: str) -> bool:
        return self.handle_with_relogin(super(SwarmClient, self).user_follow, user_id)
