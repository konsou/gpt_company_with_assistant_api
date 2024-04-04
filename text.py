from typing import Callable

from colorama import Fore, Style

from colorama import Fore as Color


def print_in_color(text: str, color: Color) -> None:
    print(f"{color}{text}{Style.RESET_ALL}")


def print_system_message(msg: str) -> None:
    print(f"{Fore.LIGHTCYAN_EX}{msg}{Style.RESET_ALL}")


def print_employee_text(msg: str) -> None:
    print(f"{Fore.GREEN}{msg}{Style.RESET_ALL}")


def print_info(msg: str) -> None:
    print_in_color(msg, Color.LIGHTCYAN_EX)


def print_warning(msg: str) -> None:
    print(f"{Fore.YELLOW}{msg}{Style.RESET_ALL}")


def print_error(msg: str) -> None:
    print_in_color(msg, Color.LIGHTRED_EX)


def print_in_box(text: str, print_function: Callable = print):
    length = len(text)
    top = f'┏{"━" * (length + 2)}┓'
    middle = f"┃ {text} ┃"
    bottom = f'┗{"━" * (length + 2)}┛'

    print_function(top)
    print_function(middle)
    print_function(bottom)
