# ../victim_stats/config.py

"""Creates server configuration and user settings."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python
import colors
from config.manager import ConfigManager
from core import SOURCE_ENGINE

# Plugin
from . import victim_stats_strings
from .info import info


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
# Get all available options
display_type_options = sorted(
    item for item in victim_stats_strings
    if item.startswith('default_display_type:')
)
distance_type_options = sorted(
    item for item in victim_stats_strings
    if item.startswith('default_distance_type:')
)


# =============================================================================
# >> CONFIGURATION
# =============================================================================
# Set the base color variables
attacker_color = None
wounded_color = None
killed_color = None
killer_color = None

# Create the victim_stats.cfg file and execute it upon __exit__
with ConfigManager(filepath=info.name, cvar_prefix='vs') as config:

    # Create the default display type convar
    display_type = config.cvar(
        name='default_display_type',
        default=1,
        description=victim_stats_strings['default_display_type'],
    )

    # Add all options for the default display type
    for _item in display_type_options:
        display_type.Options.append(
            '{value} - {text}'.format(
                value=_item,
                text=victim_stats_strings[_item].get_string()
            )
        )

    # Create the default distance type convar
    distance_type = config.cvar(
        name='default_distance_type',
        default=2,
        description=victim_stats_strings['default_distance_type']
    )

    # Add all options for the default display type
    for _item in distance_type_options:
        distance_type.Options.append(
            '{value} - {text}'.format(
                value=_item,
                text=victim_stats_strings[_item].get_string()
            )
        )

    if SOURCE_ENGINE == 'orangebox':

        config.section('Chat Color Options')
        config.text('')
        _color_options = victim_stats_strings['Options']
        _color_options.tokens = {'colors': '\n\t'.join(list(colors.__all__))}
        for line in _color_options.get_string().splitlines():
            config.text(line)

        attacker_color = config.cvar(
            name='attacker_color',
            default='255,0,0',
            description=victim_stats_strings['Attacker Color'],
        )

        wounded_color = config.cvar(
            name='wounded_color',
            default='255,0,0',
            description=victim_stats_strings['Wounded Color'],
        )

        killed_color = config.cvar(
            name='killed_color',
            default='255,0,0',
            description=victim_stats_strings['Killed Color'],
        )

        killer_color = config.cvar(
            name='killer_color',
            default='255,0,0',
            description=victim_stats_strings['Killer Color'],
        )
