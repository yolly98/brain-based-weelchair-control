from datetime import datetime

RED_COLOR = '\033[91m'
GREEN_COLOR = '\033[92m'
YELLOW_COLOR = '\033[93m'
BLUE_COLOR = '\033[94m'
PURPLE_COLOR = '\033[95m'
CYAN_COLOR = '\033[96m'
WHITE_COLOR = '\033[97m'
DEFAULT_COLOR = '\x1b[0m'


def error(msg: str) -> None:
    print(f'({datetime.now().strftime("%H:%M:%S.%f")}) {RED_COLOR}[-] {msg}{DEFAULT_COLOR}')


def warning(msg: str) -> None:
    print(f'({datetime.now().strftime("%H:%M:%S.%f")}) {YELLOW_COLOR}[!] {msg}{DEFAULT_COLOR}')


def info(msg: str) -> None:
    print(f'({datetime.now().strftime("%H:%M:%S.%f")}) {CYAN_COLOR}[i] {msg}{DEFAULT_COLOR}')


def success(msg: str) -> None:
    print(f'({datetime.now().strftime("%H:%M:%S.%f")}) {GREEN_COLOR}[+] {msg}{DEFAULT_COLOR}')
