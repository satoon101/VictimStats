# ../victim_stats/config.py

"""Creates server configuration and user settings."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Colors
import colors
#   Config
from config.manager import ConfigManager
#   Core
from core import SOURCE_ENGINE

# Script Imports
from victim_stats import victim_stats_strings
from victim_stats.info import info


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
# Get all available options
type_options = sorted(item for item in victim_stats_strings if item.isdigit())


# =============================================================================
# >> CONFIGURATION
# =============================================================================
# Set the base color variables
attacker_color = None
wounded_color = None
killed_color = None
killer_color = None

# Create the victim_stats.cfg file and execute it upon __exit__
with ConfigManager(info.basename) as config:

    # Create the default stats type convar
    default_type = config.cvar(
        'vs_default_type', '1', 0,
        victim_stats_strings['Default Type'])

    # Loop through all options
    for _item in type_options:

        # Add the option to the cfg
        default_type.Options.append('{0} - {1}'.format(
            _item, victim_stats_strings[_item].get_string()))

    if SOURCE_ENGINE == 'orangebox':

        config.section('Chat Color Options')
        config.text('')
        _color_options = victim_stats_strings['Options']
        _color_options.tokens = {'colors': '\n\t'.join(list(colors.__all__))}
        for line in _color_options.get_string().splitlines():
            config.text(line)

        attacker_color = config.cvar(
            'vs_attacker_color', '255,0,0', 0,
            victim_stats_strings['Attacker Color'])

        wounded_color = config.cvar(
            'vs_wounded_color', '255,0,0', 0,
            victim_stats_strings['Wounded Color'])

        killed_color = config.cvar(
            'vs_killed_color', '255,0,0', 0,
            victim_stats_strings['Killed Color'])

        killer_color = config.cvar(
            'vs_killer_color', '255,0,0', 0,
            victim_stats_strings['Killer Color'])
