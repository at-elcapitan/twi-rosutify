from dataclasses import dataclass

import twikit
from sqlalchemy.ext.asyncio import AsyncSession

from ..utils import check_loaded_sync, check_loaded
from ..logger import logger
from ..db import get_session, notify_entity as notify_entity_db, fetched_entity as fetched_entity_db, scheme


@dataclass
class TwiAccountTweets:
    internal_id: int
    username: str
    name: str
    tweets: list[twikit.Tweet]


class TwiAccountLazy:
    def __init__(
        self,
        twi_username: str | None,
        twi_id: int | None
    ):
        if not any ([twi_username, twi_id]):
            raise ValueError("At least one argument must be provided")

        self._seen_tweets: set[int] = set()
        self._loaded = False

        self._twi_username: str | None = twi_username
        self._twi_id: int | None = twi_id
        self._twi_name: str | None = None
        self._internal_id: int | None = None

    async def load_ids(self, session: AsyncSession) -> None:
        fetched_ids = await fetched_entity_db.get_fetched_entities_ids_unique(
            session,
            self._internal_id
        )

        logger.debug(
            "Loaded seen tweets for user=%s count=%d", 
            self._twi_username, 
            len(fetched_ids)
        )

        self._seen_tweets = set(fetched_ids)

    @get_session
    async def load_user(self, client: twikit.Client, session: AsyncSession) -> None:
        """
        RAISES
            ValueError - client was unable to load user
        """
        notify_entity: scheme.NotifyEntity | None = None

        if self._twi_username is not None:
            notify_entity = await notify_entity_db.get_notify_entity_by_username(
                session,
                self._twi_username
            )
        elif self._twi_id is not None:
            notify_entity = await notify_entity_db.get_notify_entity_by_id(
                session,
                self._twi_id
            )

        if notify_entity is not None:
            self._twi_username = notify_entity.twi_username
            self._twi_id = notify_entity.twi_id
            self._twi_name = notify_entity.twi_name
            self._internal_id = notify_entity.id
            self._loaded = True

            logger.debug(
                "User loaded from DB: %s (id=%d)", 
                self._twi_username, 
                self._twi_id
            )

            await self.load_ids(session)
            return

        user: twikit.User = None

        if self._twi_username is not None:
            user = await client.get_user_by_screen_name(self._twi_username)
        else:
            user = await client.get_user_by_id(self._twi_id)

        if user is None:
            raise ValueError(
                f"User "
                f"{self._twi_username if self._twi_username is not None else self._twi_id}"
                 " could not be loaded"
            )
        
        notify_entity = await notify_entity_db.create_notify_entity(
            session,
            twi_id=user.id,
            twi_username=user.screen_name,
            twi_name=user.name
        )

        logger.debug(
            "User loaded from API: %s (id=%s)", 
            user.screen_name, 
            user.id
        )
        
        self._twi_username = user.screen_name
        self._twi_name = user.name
        self._twi_id = user.id
        self._internal_id = notify_entity.id
        self._loaded = True

        await self.load_ids(session)

    @check_loaded
    async def get_latest_tweets(
        self,
        client: twikit.Client,
        count: int = 20
    ) -> TwiAccountTweets:
        """
        RAISES
            ValueError - client was not lazy loaded
        """
        ret: list[twikit.Tweet] = []

        tweets = await client.get_user_tweets(
            user_id=str(self._twi_id),
            tweet_type="Tweets",
            count=count
        )

        for tweet in tweets:
            if int(tweet.id) not in self._seen_tweets:
                ret.append(tweet) 
                self._seen_tweets.add(int(tweet.id))

        logger.debug(
            "Tweets loaded for user=%s new=%d total_seen=%d", 
            self._twi_username, 
            len(ret), 
            len(self._seen_tweets)
        )

        return TwiAccountTweets(
            internal_id=self._internal_id,
            username=self._twi_username,
            name=self._twi_name,
            tweets=ret
        )
    
    @check_loaded_sync
    def get_id(self) -> int:
        return self._twi_id