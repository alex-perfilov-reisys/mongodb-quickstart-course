import datetime

from dateutil import parser

from infrastructure.switchlang import switch
import program_hosts as hosts
from program_hosts import success_msg, error_msg
import infrastructure.state as state
import services.data_service as svc


def run():
    print(' ****************** Welcome guest **************** ')
    print()

    show_commands()

    while True:
        action = hosts.get_action()

        with switch(action) as s:
            s.case('c', hosts.create_account)
            s.case('l', hosts.log_into_account)

            s.case('a', add_a_snake)
            s.case('y', view_your_snakes)
            s.case('b', book_a_cage)
            s.case('v', view_bookings)
            s.case('m', lambda: 'change_mode')

            s.case('?', show_commands)
            s.case('', lambda: None)
            s.case(['x', 'bye', 'exit', 'exit()'], hosts.exit_app)

            s.default(hosts.unknown_command)

        state.reload_account()

        if action:
            print()

        if s.result == 'change_mode':
            return


def show_commands():
    print('What action would you like to take:')
    print('[C]reate an account')
    print('[L]ogin to your account')
    print('[B]ook a cage')
    print('[A]dd a snake')
    print('View [y]our snakes')
    print('[V]iew your bookings')
    print('[M]ain menu')
    print('e[X]it app')
    print('[?] Help (this info)')
    print()


def add_a_snake():
    print(' ****************** Add a snake **************** ')
    if not state.active_account:
        error_msg("Log in first")
        return

    name = input("What's your snake's name? ")
    if not name:
        error_msg("Cancelled")
        return
    length = float(input("Your snake's length (meters): "))
    species = input("Species? ")
    is_venomous = input("Is your snake venomous? [y/n]").lower().startswith('y')

    snake = svc.add_snake(state.active_account, name, length, species, is_venomous)
    state.reload_account()
    success_msg(f"Success! Created snake {snake.name}")


def view_your_snakes():
    print(' ****************** Your snakes **************** ')
    if not state.active_account:
        error_msg("Log in first")
        return

    snakes = svc.get_snakes_for_user()
    print("You have {} snakes.".format(len(snakes)))

    for s in snakes:
        print(f" * Snake `{s.name}` is {s.length}m long and is {'not ' if not s.is_venomous else ''}venomous.")


def book_a_cage():
    print(' ****************** Book a cage **************** ')
    if not state.active_account:
        error_msg("Log in first")
        return

    snakes = svc.get_snakes_for_user()
    if not snakes:
        error_msg("You must [a]dd a snake first.")
        return

    print("Let's find available cages.")
    start_date = parser.parse(input("Check-in date (yyyy-mm-dd): "))
    end_date = parser.parse(input("Check-out date (yyyy-mm-dd): "))
    if not start_date or not end_date:
        error_msg("Cancelled")
        return

    if start_date >= end_date:
        error_msg("Check-in date must be before check-out date")
        return

    print()

    for num, s in enumerate(snakes):
        print(f" {num + 1}. Snake `{s.name}` is {s.length}m long and is {'not ' if not s.is_venomous else ''}venomous.")

    snake = snakes[int(input("Which snake needs a cage? ")) - 1]

    cages = svc.get_available_cages(start_date, end_date, snake)

    if cages:
        success_msg("These cages available for you:")
    else:
        error_msg("No cages available, sorry.")
        return

    for num, c in enumerate(cages):
        print(f"  {num + 1}. Cage {c.name}, {c.square_meters} square meters, ${c.price} per day")

    print()
    cage = cages[int(input("Which cage would you like to book? ")) - 1]
    if not cage:
        error_msg("Wrong number. Cancelling.")
        return

    print(f"Booking cage `{cage.name}`...")

    booked = svc.book_cage(cage, snake, start_date, end_date)
    if booked:
        success_msg("Congrats! Your cage is booked!")
    else:
        error_msg("Sorry we could not book your cage")


def view_bookings():
    print(' ****************** Your bookings **************** ')
    if not state.active_account:
        error_msg("Log in first")
        return

    snakes = {s.id: s for s in svc.get_snakes_for_user()}
    bookings = svc.get_bookings_for_user()

    if not bookings:
        error_msg("No bookings found")
        return

    success_msg("We found these bookings: ")
    for b in bookings:
        print("  * Snake `{}` into cage `{}` from {} to {} ({} days) for ${}/night".format(
            snakes.get(b.guest_snake_id).name,
            b.cage.name,
            b.check_in_date.strftime('%Y-%m-%d'),
            b.check_out_date.strftime('%Y-%m-%d'),
            (b.check_out_date - b.check_in_date).days,
            b.cage.price
        ))
