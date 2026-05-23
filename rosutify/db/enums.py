from enum import Enum

class Role(str, Enum):
    admin = "Admin"
    fetcher = "Fetcher"