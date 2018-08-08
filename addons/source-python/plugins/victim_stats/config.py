# ../victim_stats/config.py

"""Creates server configuration and user settings."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python
from config.manager import ConfigManager

# Plugin
from .info import info
from .strings import CONFIG_STRINGS


# =============================================================================
# >> ALL DECLARATION
# =============================================================================
__all__ = (
    'display_type',
    'display_type_options',
    'distance_type',
    'distance_type_options',
)


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
# Get all available options
display_type_options = sorted(
    item for item in CONFIG_STRINGS
    if item.startswith('default_display_type:')
)
distance_type_options = sorted(
    item for item in CONFIG_STRINGS
    if item.startswith('default_distance_type:')
)


# =============================================================================
# >> CONFIGURATION
# =============================================================================
# Create the victim_stats.cfg file and execute it upon __exit__
with ConfigManager(info.name, 'vs_') as config:

    # Create the default display type convar
    display_type = config.cvar(
        name='default_display_type',
        default=1,
        description=CONFIG_STRINGS['default_display_type'],
    )

    # Add all options for the default display type
    for _item in display_type_options:
        display_type.Options.append(
            f'{_item} - {CONFIG_STRINGS[_item].get_string()}'
        )

    # Create the default distance type convar
    distance_type = config.cvar(
        name='default_distance_type',
        default=2,
        description=CONFIG_STRINGS['default_distance_type']
    )

    # Add all options for the default display type
    for _item in distance_type_options:
        distance_type.Options.append(
            f'{_item} - {CONFIG_STRINGS[_item].get_string()}'
        )
