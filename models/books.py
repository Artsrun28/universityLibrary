from .db import database
from peewee import CharField, IntegerField


class Book(database.Model):
    book_name = CharField()
    author_name = CharField()
    release_year = IntegerField()
    book_copy = IntegerField()

    def __str__(self):
        return f'({self. book_name}, By {self.author_name}, Released in {self.release_year})'

    def __repr__(self):
        return self.__str__()
