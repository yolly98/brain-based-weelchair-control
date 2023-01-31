from datetime import datetime

RED_COLOR = '\033[0;91m'
GREEN_COLOR = '\033[2;92m'
YELLOW_COLOR = '\033[0;93m'
BLUE_COLOR = '\033[0;94m'
PURPLE_COLOR = '\033[0;95m'
CYAN_COLOR = '\033[0;96m'
WHITE_COLOR = '\x1b[0;37m'
DEFAULT_COLOR = '\x1b[0m'


def error(msg: str) -> None:
    print(f'{DEFAULT_COLOR}({datetime.now().strftime("%H:%M:%S.%f")}) {RED_COLOR}[-] {msg}{DEFAULT_COLOR}')


def warning(msg: str) -> None:
    print(f'{DEFAULT_COLOR}({datetime.now().strftime("%H:%M:%S.%f")}) {YELLOW_COLOR}[!] {msg}{DEFAULT_COLOR}')


def info(msg: str) -> None:
    print(f'{DEFAULT_COLOR}({datetime.now().strftime("%H:%M:%S.%f")}) {CYAN_COLOR}[i] {msg}{DEFAULT_COLOR}')


def trace(msg: str) -> None:
    print(f'{DEFAULT_COLOR}({datetime.now().strftime("%H:%M:%S.%f")}){DEFAULT_COLOR} {msg}{DEFAULT_COLOR}')


def success(msg: str) -> None:
    print(f'{DEFAULT_COLOR}({datetime.now().strftime("%H:%M:%S.%f")}) {GREEN_COLOR}[+] {msg}{DEFAULT_COLOR}')
