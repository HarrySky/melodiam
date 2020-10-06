from orm import Integer, Model, Text  # type: ignore[import]
from orm.exceptions import NoMatch  # type: ignore[import]
from tekore import Token as TekoreToken  # type: ignore[import]

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

    @staticmethod
    async def upsert(user_id: str, token: TekoreToken) -> None:
        try:
            token_row: Token = await Token.objects.get(
                user_id=user_id, scope=str(token.scope)
            )
            await token_row.update(
                access=token.access_token,
                refresh=token.refresh_token,
                expires_at=token.expires_at,
            )
        except NoMatch:
            await Token.objects.create(
                user_id=user_id,
                scope=str(token.scope),
                access=token.access_token,
                refresh=token.refresh_token,
                expires_at=token.expires_at,
            )
