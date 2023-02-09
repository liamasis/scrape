import logging

class Colors:
    PURPLE_BOLD = '\033[1;35m';
    PURPLE = '\033[0;35m';
    YELLOW_BOLD = '\033[1;33m';
    RED_BOLD = '\033[1;31m';
    RED = '\033[0;31m';
    GREEN_BOLD = '\033[1;32m';
    GREEN = '\033[0;32m';
    BLUE_BOLD = '\033[1;34m';
    BLUE = '\033[0;34m';
    CYAN_BOLD = '\033[1;36m';
    CYAN = '\033[0;36m';

    BOLD = '\033[1m';
    RESET = '\033[0m';


def colorify(text, color):
    return f'{color}{text}{Colors.RESET}'
