# auto-generated snapshot
from peewee import *
import datetime
import peewee


snapshot = Snapshot()


@snapshot.append
class Book(peewee.Model):
    book_name = CharField(max_length=255)
    author_name = CharField(max_length=255)
    release_year = IntegerField()
    book_copy = IntegerField()
    class Meta:
        table_name = "book"


@snapshot.append
class LibraryHistory(peewee.Model):
    student_id = IntegerField()
    student_name = CharField(max_length=255)
    book_name = CharField(max_length=255)
    author_name = CharField(max_length=255)
    date_taken = DateField()
    return_date = DateField()
    returned = BooleanField(default=False)
    class Meta:
        table_name = "libraryhistory"


@snapshot.append
class User(peewee.Model):
    username = CharField(max_length=50)
    password = CharField(max_length=255)
    full_name = CharField(max_length=255)
    email = CharField(max_length=255)
    role = CharField(max_length=255)
    class Meta:
        table_name = "user"


def forward(old_orm, new_orm):
    libraryhistory = new_orm['libraryhistory']
    return [
        # Apply default value False to the field libraryhistory.returned,
        libraryhistory.update({libraryhistory.returned: False}).where(libraryhistory.returned.is_null(True)),
    ]
