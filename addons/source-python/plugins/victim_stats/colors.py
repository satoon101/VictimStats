# ../victim_stats/colors.py

"""Contains all translation variables for the base plugin."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python
from colors import DARK_BLUE, DARK_RED, LIGHT_BLUE, LIGHT_RED
from core import GAME_NAME


# =============================================================================
# >> ALL DECLARATION
# =============================================================================
__all__ = (
    'ATTACKER_COLOR',
    'KILLED_COLOR',
    'KILLER_COLOR',
    'WOUNDED_COLOR',
)


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
if GAME_NAME == 'csgo':
    # ATTACKER_COLOR = '\x07'
    ATTACKER_COLOR = '\x0F'
    WOUNDED_COLOR = '\x0C'
    KILLED_COLOR = '\x0A'
    KILLER_COLOR = '\x02'
else:
    ATTACKER_COLOR = DARK_RED
    WOUNDED_COLOR = DARK_BLUE
    KILLED_COLOR = LIGHT_BLUE
    KILLER_COLOR = LIGHT_RED
