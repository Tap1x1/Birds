from tokenize import Double
from pony import orm
from pony.orm import Database,Required,Set,Json,PrimaryKey,Optional
from pony.orm.core import db_session
import datetime

db = Database()
db.bind(provider='sqlite', filename='//data/data/ru.travelfood.simple_ui/databases/Birds', create_db=True)


class SW_Birds(db.Entity):
    name = Required(str)
    color = Optional(str)
    pictures = Optional(Json)
    seen = Optional(int)
    created_at = Optional(datetime.datetime, sql_default='CURRENT_TIMESTAMP')
    number_of_sightings = Optional(int)

class SW_SeenBirds(db.Entity):
    name = Required(str)
    color = Optional(str)
    pictures = Optional(Json)
    seen = Optional(int)
    number_of_sightings = Optional(int)
    created_at = Optional(datetime.datetime, sql_default='CURRENT_TIMESTAMP')


def init():
    db.generate_mapping(create_tables=True)




