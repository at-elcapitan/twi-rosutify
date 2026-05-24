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
        password: str
    ) -> None:
        await self._client.login(auth_info_1=username, auth_info_2=email, password=password)
        self._loaded = True

    @check_loaded
    async def add_account(self, account: TwiAccountLazy) -> None:
        """
        RAISES
            ValueError - from load_user in TwiAccountLazy
        """

        await account.load_user(self._client)
        self._listened_accounts[account.get_id()] = account

    @check_loaded_sync
    def add_community(self, account_id: int, community_id: int) -> None:
        """
        RAISES
            IndexError - account_id was not found
        """
        account = self._listened_accounts[account_id]
        account.subscribe_community(community_id)

    @check_loaded
    async def load_tweets():
        pass