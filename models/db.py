from peewee import PostgresqlDatabase
from config import AppConfig

database = PostgresqlDatabase(AppConfig.DATABASE_NAME,
                              user=AppConfig.DATABASE_USER,
                              password=AppConfig.DATABASE_PASS,
                              host=AppConfig.DATABASE_HOST,
                              port=AppConfig.DATABASE_PORT,
                              )
