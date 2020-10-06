from databases import Database
from sqlalchemy import MetaData  # type: ignore[import]

from melodiam import conf

database = Database(conf.DATABASE_URL, force_rollback=conf.TESTING)
metadata = MetaData()
