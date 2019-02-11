import mongoengine
import datetime

from data.bookings import Booking


class Cage(mongoengine.Document):
    registered_date = mongoengine.DateTimeField(default=datetime.datetime.now)

    name = mongoengine.StringField(required=True)
    price = mongoengine.StringField(required=True)
    is_carpeted = mongoengine.StringField(required=True)
    has_toys = mongoengine.StringField(required=True)
    allow_dangerous_snakes = mongoengine.StringField(required=True)

    bookings = mongoengine.EmbeddedDocumentListField(Booking)

    meta = {
        'db_alias': 'core',
        'collection': 'cages'
    }
