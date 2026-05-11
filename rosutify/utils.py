from datetime import datetime

from aiogram import __version__ as aiogram_version
from twikit import __version__ as twikit_version

from tgcient import (
    __version__  as current_version, 
    __codename__ as current_codename
)

from datetime import datetime

class Colors:
    HEADER    = '\033[95m'
    BLUE      = '\033[94m'
    CYAN      = '\033[96m'
    GREEN     = '\033[92m'
    YELLOW    = '\033[93m'
    BOLD      = '\033[1m'
    DIM       = '\033[2m'
    RESET     = '\033[0m'

def print_info():
    print(f"{Colors.BLUE}╭───────────────────────────────────────╮{Colors.RESET}")
    print(f"{Colors.BLUE}│  {Colors.BOLD}{Colors.HEADER}Rosutify{Colors.RESET} {Colors.CYAN}v{current_version}{Colors.RESET} \"{Colors.YELLOW}{current_codename}{Colors.RESET}\"               {Colors.BLUE}│{Colors.RESET}")
    print(f"{Colors.BLUE}├───────────────────────────────────────┤{Colors.RESET}")
    print(f"{Colors.BLUE}│  {Colors.BOLD}Dependencies:                        {Colors.BLUE}│{Colors.RESET}")
    print(f"{Colors.BLUE}│  {Colors.GREEN}-{Colors.RESET} Aiogram:  {Colors.CYAN}v{aiogram_version}                  {Colors.BLUE}│{Colors.RESET}")
    print(f"{Colors.BLUE}│  {Colors.GREEN}-{Colors.RESET} Twikit:   {Colors.CYAN}v{twikit_version}                   {Colors.BLUE}│{Colors.RESET}")
    print(f"{Colors.BLUE}│                                       {Colors.BLUE}│{Colors.RESET}")
    print(f"{Colors.BLUE}│  {Colors.RESET}{Colors.DIM}Started at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}{Colors.RESET}      {Colors.BLUE}│{Colors.RESET}")
    print(f"{Colors.BLUE}╰───────────────────────────────────────╯{Colors.RESET}")