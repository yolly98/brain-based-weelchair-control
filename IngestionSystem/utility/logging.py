from datetime import datetime

RED_COLOR = "\033[91m"
GREEN_COLOR = "\033[92m"
YELLOW_COLOR = "\033[93m"
BLUE_COLOR = "\033[94m"
PURPLE_COLOR = "\033[95m"
CYAN_COLOR = "\033[96m"
WHITE_COLOR = "\033[97m"
DEFAULT_COLOR = WHITE_COLOR


def error(msg: str) -> None:
    print(f'({datetime.now().strftime("%H:%M:%S.%f")}) {RED_COLOR}[-] {msg} {DEFAULT_COLOR}')


def warning(msg: str) -> None:
    print(f'({datetime.now().strftime("%H:%M:%S.%f")}) {YELLOW_COLOR}[!] {msg} {DEFAULT_COLOR}')


def warning_simulation(uuid, msg: str) -> None:
    print(f'({uuid}) {YELLOW_COLOR} {msg} {DEFAULT_COLOR}')


def info(msg: str, info_type: int) -> None:
    if info_type == 0:
        print(f'({datetime.now().strftime("%H:%M:%S.%f")}) {CYAN_COLOR}[i] {msg} {DEFAULT_COLOR}')
    elif info_type == 1:
        print(f'({datetime.now().strftime("%H:%M:%S.%f")}) {BLUE_COLOR}[i] {msg} {DEFAULT_COLOR}')
    elif info_type == 2:
        print(f'{BLUE_COLOR}{msg} {DEFAULT_COLOR}')


def info_simulation(uuid: str, msg: str, info_type: int) -> None:
    if info_type == 0:
        print(f'{CYAN_COLOR}{msg}{DEFAULT_COLOR}')
    elif info_type == 1:
        print(f'({uuid}) {BLUE_COLOR} {msg} {DEFAULT_COLOR}')
    elif info_type == 2:
        print(f'{BLUE_COLOR}{msg} {DEFAULT_COLOR}')


def trace(msg: str) -> None:
    print(f'({datetime.now().strftime("%H:%M:%S.%f")}){DEFAULT_COLOR} {msg} {DEFAULT_COLOR}')


def success(msg: str) -> None:
    print(f'({datetime.now().strftime("%H:%M:%S.%f")}) {GREEN_COLOR}[+] {msg} {DEFAULT_COLOR}')
