from orm import Integer, Model, Text  # type: ignore[import]

from melodiam.resources import database, metadata


class Token(Model):
    __tablename__ = "tokens"
    __database__ = database
    __metadata__ = metadata

    id = Integer(primary_key=True)
    user_id = Text()
    scope = Text(allow_blank=True)
    access = Text()
    refresh = Text()
    expires_at = Integer()
