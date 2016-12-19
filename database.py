from peewee import *
from playhouse.postgres_ext import *
import urllib.parse

db_uri = urllib.parse.urlparse("postgres://postgres@localhost/postgres")

db = PostgresqlExtDatabase(
    database=db_uri.path[1:],
    host=db_uri.hostname,
    user=db_uri.username,
    password=db_uri.password,
    register_hstore=False
)

class Summary(Model):
    topic = CharField(max_length=2048)
    word_limit = IntegerField()
    summary = TextField()
    last_updated = DateField()
    images = ArrayField(TextField)
    links = ArrayField(TextField)
    names = ArrayField(TextField)


    class Meta:
        database = db

if __name__ == "__main__":
    db.create_tables([Summary])
