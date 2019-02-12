from colorama import Fore
from dateutil import parser

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
    print('[A]uth')
    print('[L]ist cages')
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
    carpeted = input("Has a carpet? [y/n] ").lower().startswith('y')
    has_toys = input("Has toys? [y/n] ").lower().startswith('y')
    allow_dangerous = input("Allow venomous snakes? [y/n] ").lower().startswith('y')
    name = input("New cage name: ")
    price = input("Price: ")

    cage = svc.register_cage(
        state.active_account,
        name,
        allow_dangerous,
        has_toys,
        carpeted,
        meters,
        price
    )

    state.reload_account()
    success_msg(f"Cage is created with id {cage.id}")


def list_cages(supress_header=False):
    if not supress_header:
        print(' ******************     Your cages     **************** ')

    cages = svc.find_cages_for_user(state.active_account)
    print(f"You have {len(cages)} cages.")
    for num, c in enumerate(cages):
        print(f" {num + 1}. {c.name} in {c.square_meters} meters.")
        for b in c.bookings:
            print("    * Bookings: {},{} days, booked? {}".format(
                b.check_in_date, (b.check_out_date - b.check_in_date).days,
                'YES' if b.booked_date is not None else 'no'))


def update_availability():
    print(' ****************** Add available date **************** ')

    if not state.active_account:
        error_msg("Log in first")
        return

    list_cages(supress_header=True)

    cage_number = input("Enter cage #: ")

    if not cage_number.split():
        error_msg("Cancelled")
        print()
        return

    cage_number = int(cage_number)

    cages = svc.find_cages_for_user(state.active_account)
    selected_cage = cages[cage_number - 1]

    success_msg("Selected cage {}".format(selected_cage.name))

    start_date = parser.parse(
        input("Enter available date [yyyy-mm-dd]: ")
    )
    days = int(input("How many days available to block? "))

    svc.add_available_date(
        selected_cage, start_date, days
    )
    state.reload_account()

    success_msg(f"Success! Dates added for cage {selected_cage.name}")


def view_bookings():
    print(' ****************** Your bookings **************** ')

    if not state.active_account:
        error_msg("Log in first")
        return

    cages = svc.find_cages_for_user(state.active_account)

    bookings = [
        (c, b)
        for c in cages
        for b in c.bookings
        if b.booked_date is not None
    ]

    if not bookings:
        error_msg("Nothing booked")
        return

    print(f"You have {len(bookings)} bookings:")

    for c, b in bookings:
        print('  * Cage `{}`, booked from {} to {} ({} days).'.format(
            c.name,
            b.check_in_date.strftime('%Y-%m-%d'),
            b.check_out_date.strftime('%Y-%m-%d'),
            b.duration_in_days.days
        ))


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
