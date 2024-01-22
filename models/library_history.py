from .db import database
from peewee import CharField, IntegerField, DateField, BooleanField


class LibraryHistory(database.Model):
    student_id = IntegerField()
    student_name = CharField()
    book_name = CharField()
    author_name = CharField()
    date_taken = DateField()
    return_date = DateField()
    returned = BooleanField(default=False)

    class Meta:
        database = database
