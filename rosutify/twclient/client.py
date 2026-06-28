import twikit

from ..utils import check_loaded, check_loaded_sync
from .fetch_account import TwiAccountLazy
from ..event import event_bus

class ClientWrapper:
    def __init__(self, lang: str = 'en-US') -> None:
        self._client = twikit.Client(lang)
        self._loaded = False
        
        self._listened_accounts: dict[int, TwiAccountLazy] = {}

    async def load_client(
        self,
        username: str,
        email: str | None,
        password: str,
        cookies_path: str | None = None
    ) -> None:
        await self._client.login(auth_info_1=username, auth_info_2=email, password=password, cookies_file=cookies_path)
        self._loaded = True

    @check_loaded
    async def add_account(self, account: TwiAccountLazy) -> None:
        """
        RAISES
            ValueError - from load_user in TwiAccountLazy
        """

        await account.load_user(self._client)
        self._listened_accounts[account.get_id()] = account

        return account

    @check_loaded
    async def load_tweets(self):
        for account in self._listened_accounts.values():
            account_tweets = await account.get_latest_tweets(self._client)

            if len(account_tweets.tweets) > 0:
                await event_bus.emit("new_tweets", account_tweets)