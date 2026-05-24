import twikit

from ..utils import check_loaded_sync, check_loaded

class TwiAccountLazy:
    def __init__(
        self,
        twi_username: str | None,
        twi_id: int | None
    ):
        if not any ([twi_username, twi_id]):
            raise ValueError("At least one argument must be provided")
        
        self._subscribed_communities: set[int] = set()
        self._seen_tweets: set[int] = set()
        self._loaded = False

        self._twi_username: str | None = twi_username
        self._twi_id: int | None = twi_id
        self._twi_name: str | None = None

    async def load_user(self, client: twikit.Client) -> None:
        """
        RAISES
            ValueError - client was unable to load user
        """
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
        
        self._twi_username = user.screen_name
        self._twi_name = user.name
        self._twi_id = user.id
        self._loaded = True

    @check_loaded
    async def get_latest_tweets(
        self,
        client: twikit.Client,
        count: int = 20
    ) -> list[twikit.Tweet]:
        """
        RAISES
            ValueError - client was not lazy loaded
        """
        
        ret: list[twikit.Tweet] = []
        tweets = await client.get_user_tweets(
            user_id=self._twi_id,
            tweet_type={"Media", "Replies", "Tweets"},
            count=count
        )

        for tweet in tweets:
            if tweet.id not in self._seen_tweets:
                ret.append(tweet)
                self._seen_tweets.add(tweet.id)

        return ret
    
    @check_loaded_sync
    def get_id(self) -> int:
        return self._twi_id

    def subscribe_community(self, community_id: int) -> None:
        self._subscribed_communities.add(community_id)

    def unsubscribe_community(self, community_id: int) -> None:
        self._subscribed_communities.remove(community_id)

    def get_subscribed_communities(self) -> set[int]:
        return self._subscribed_communities