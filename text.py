from typing import Callable

from colorama import Fore, Style


def print_system_message(msg: str) -> None:
    print(f"{Fore.LIGHTCYAN_EX}{msg}{Style.RESET_ALL}")


def print_employee_text(msg: str) -> None:
    print(f"{Fore.GREEN}{msg}{Style.RESET_ALL}")


def print_warning(msg: str) -> None:
    print(f"{Fore.YELLOW}{msg}{Style.RESET_ALL}")


def print_in_box(text: str, print_function: Callable = print):
    length = len(text)
    top = f'┏{"━" * (length + 2)}┓'
    middle = f'┃ {text} ┃'
    bottom = f'┗{"━" * (length + 2)}┛'

    print_function(top)
    print_function(middle)
    print_function(bottom)
