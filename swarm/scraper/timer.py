import logging

from .colors import Colors, colorify
import time

logger = logging.getLogger(__name__)

class TimerError(Exception):
    """A custom exception used to report errors in use of Timer class"""

class Timer:
    def __init__(self):
        self._t0 = None
        self._comment = None

    def start(self, comment=None, print=True):

        self._comment = comment
        self._t0 = time.time_ns()

        if print:
            logger.info(colorify(f'{comment}...', Colors.BLUE))

    def stop(self):
        """Stop the timer, and report the elapsed time"""
        t1 = time.time_ns()

        if self._t0 is None:
            return

        if self._comment:
            logger.info(colorify(f"{self._comment} took {(t1 - self._t0) / 10 ** 6} ms", Colors.PURPLE_BOLD))
        else:
            logger.info(colorify(f"Took {(t1 - self._t0) / 10 ** 6} ms", Colors.PURPLE_BOLD))

        self._t0 = None
        self._comment = None
