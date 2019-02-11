from colorama import Fore
from infrastructure.switchlang import switch
import infrastructure.state as state
import services.data_service as svc


def run():
    print(' ****************** Welcome host **************** ')
    print()

    show_commands()

    while True:
        action = get_action()

        with switch(action) as s:
            s.case('c', create_account)
            s.case('a', log_into_account)
            s.case('l', list_cages)
            s.case('r', register_cage)
            s.case('u', update_availability)
            s.case('v', view_bookings)
            s.case('m', lambda: 'change_mode')
            s.case(['x', 'bye', 'exit', 'exit()'], exit_app)
            s.case('?', show_commands)
            s.case('', lambda: None)
            s.default(unknown_command)

        if action:
            print()

        if s.result == 'change_mode':
            return


def show_commands():
    print('What action would you like to take:')
    print('[C]reate an account')
    print('[L]ogin to your account')
    print('[R]egister a cage')
    print('[U]pdate cage availability')
    print('[V]iew your bookings')
    print('Change [M]ode (guest or host)')
    print('e[X]it app')
    print('[?] Help (this info)')
    print()


def create_account():
    print(' ****************** REGISTER **************** ')

    name = input('Your name? ')
    email = input('Your email? ')

    old_account = svc.find_account_by_email(email)
    if old_account:
        error_msg(f"FATAL: email {email} already exists")
        return

    state.active_account = svc.create_account(name, email)
    success_msg(f"SUCCESS: User created with id {state.active_account.id}")


def log_into_account():
    print(' ****************** LOGIN **************** ')

    email = input("Your email?").lower().strip()
    account = svc.find_account_by_email(email)
    if not account:
        error_msg(f"Could not find user with email {email}")
        return

    state.active_account = account
    success_msg("Logged in.")


def register_cage():
    print(' ****************** REGISTER CAGE **************** ')

    if not state.active_account:
        error_msg("Log in first")
        return

    meters = input("How many square meters in the cage? ")
    if not meters:
        error_msg("Cancelled")
        return

    meters = float(meters)
    carpeted = input("Capreted? [y/n] ").lower().startswith('y')
    has_toys = input("Has toys? [y/n] ").lower().startswith('y')
    allow_dangerous = input("Allow venomous snakes? [y/n] ").lower().startswith('y')
    name = input("New cage name: ")


def list_cages(supress_header=False):
    if not supress_header:
        print(' ******************     Your cages     **************** ')

    # TODO: Require an account
    # TODO: Get cages, list details

    print(" -------- NOT IMPLEMENTED -------- ")


def update_availability():
    print(' ****************** Add available date **************** ')

    # TODO: Require an account
    # TODO: list cages
    # TODO: Choose cage
    # TODO: Set dates, save to DB.

    print(" -------- NOT IMPLEMENTED -------- ")


def view_bookings():
    print(' ****************** Your bookings **************** ')

    # TODO: Require an account
    # TODO: Get cages, and nested bookings as flat list
    # TODO: Print details for each

    print(" -------- NOT IMPLEMENTED -------- ")


def exit_app():
    print()
    print('bye')
    raise KeyboardInterrupt()


def get_action():
    text = '> '
    if state.active_account:
        text = f'{state.active_account.name}> '

    action = input(Fore.YELLOW + text + Fore.WHITE)
    return action.strip().lower()


def unknown_command():
    print("Sorry we didn't understand that command.")


def success_msg(text):
    print(Fore.LIGHTGREEN_EX + text + Fore.WHITE)


def error_msg(text):
    print(Fore.LIGHTRED_EX + text + Fore.WHITE)
