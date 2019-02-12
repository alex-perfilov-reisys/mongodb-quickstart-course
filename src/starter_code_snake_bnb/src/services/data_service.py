import datetime
from typing import List

from data.bookings import Booking
from data.cages import Cage
from data.owners import Owner
from data.snakes import Snake
from infrastructure import state


def create_account(name: str, email: str) -> Owner:
    owner = Owner()
    owner.name = name
    owner.email = email

    owner.save()

    return owner


def find_account_by_email(email: str) -> Owner:
    owner = Owner.objects(email=email).first()
    return owner


def register_cage(active_account: Owner,
                  name, allow_dangerous,
                  has_toys, carpeted, meters, price) -> Cage:
    cage = Cage()
    cage.name = name
    cage.allow_dangerous_snakes = allow_dangerous
    cage.is_carpeted = carpeted
    cage.has_toys = has_toys
    cage.square_meters = meters
    cage.price = price

    cage.save()

    account = find_account_by_email(active_account.email)
    account.cage_ids.append(cage.id)
    account.save()

    return cage


def find_cages_for_user(account: Owner) -> List[Cage]:
    query = Cage.objects(id__in=account.cage_ids)
    cages = list(query)

    return cages


def add_available_date(cage: Cage,
                       start_date: datetime.datetime, days: int):
    booking = Booking()
    booking.check_in_date = start_date
    booking.check_out_date = start_date + datetime.timedelta(days=days)

    cage = Cage.objects(id=cage.id).first()
    cage.bookings.append(booking)
    cage.save()

    return cage


def add_snake(active_account: Owner, name, length, species, is_venomous) -> Snake:
    snake = Snake()
    snake.name = name
    snake.length = length
    snake.species = species
    snake.is_venomous = is_venomous

    snake.save()

    active_account.snake_ids.append(snake.id)
    active_account.save()

    return snake


def get_snakes_for_user() -> List[Snake]:
    snakes = Snake.objects(id__in=state.active_account.snake_ids)
    return snakes


def get_available_cages(start_date: datetime.datetime, end_date: datetime.datetime,
                        snake: Snake) -> List[Cage]:
    min_size = snake.length / 4

    query = Cage.objects() \
        .filter(square_meters__gte=min_size) \
        .filter(bookings__check_in_date__lte=start_date) \
        .filter(bookings__check_out_date__gte=end_date) \
        .filter(bookings__booked_date=0)

    if snake.is_venomous:
        query = query.filter(allow_dangerous_snakes=True)

    cages = query.order_by('price', '-square_meters')
    return cages


def book_cage(cage: Cage, snake: Snake,
              start_date: datetime.datetime, end_date: datetime.datetime) -> bool:
    found = False
    for b in cage.bookings:
        if b.check_in_date <= start_date and b.check_out_date >= end_date and not b.guest_snake_id:
            b.booked_date = start_date
            b.guest_snake_id = snake.id
            b.guest_owner_id = state.active_account.id
            found = True

    if not found:
        return False

    return bool(cage.save())


def get_bookings_for_user() -> List[Booking]:
    cages = Cage.objects().filter(bookings__guest_owner_id=state.active_account.id)

    def map_cate_to_booking(cage, booking):
        booking.cage = cage
        return booking

    bookings = [
        map_cate_to_booking(cage, booking)
        for cage in cages
        for booking in cage.bookings
        if booking.guest_owner_id == state.active_account.id
    ]

    return bookings
