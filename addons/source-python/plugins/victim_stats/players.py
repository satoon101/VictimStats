# ../victim_stats/players.py

"""Stores and interacts with players."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
#   Collections
from collections import OrderedDict
from collections import defaultdict

# Source.Python Imports
#   Players
from players.entity import PlayerEntity
from players.helpers import index_from_userid
#   Settings
from settings.player import PlayerSettings

# Script Imports
from victim_stats import hitgroup_strings
from victim_stats import victim_stats_strings
from victim_stats.chat import _ChatStats
from victim_stats.config import default_type
from victim_stats.config import type_options
from victim_stats.info import info
from victim_stats.menu import _MenuStats


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
# Create the user settings
user_settings = PlayerSettings(info.name, 'vs')


class _PlayerDictionary(dict):

    """Stores players with their victim stats information."""

    def __init__(self):
        """Create the user setting and store its options."""
        # Create the setting
        self.type_setting = user_settings.add_string_setting(
            'Display Type', default_type.get_string(),
            victim_stats_strings['Type'])

        # Loop through all available options
        for item in type_options:

            # Add the option to the setting
            self.type_setting.add_option(item, victim_stats_strings[item])

    def __missing__(self, userid):
        """Create a PlayerStats instance for missing players."""
        value = self[userid] = PlayerStats(index_from_userid(userid))
        return value

    def __delitem__(self, userid):
        """Remove the player only if they are in the dictionary."""
        if userid in self:
            super(_PlayerDictionary, self).__delitem__(userid)

# Get the _PlayerDictionary instance
player_dictionary = _PlayerDictionary()


class PlayerStats(PlayerEntity, _ChatStats, _MenuStats):

    """Store victim stats information and display it when the player dies."""

    def __init__(self, index):
        """Create the base dictionaries to store victim stats information."""
        self.taken = _OrderedStats(_DamageStats)
        self.given = _OrderedStats(_DamageStats)
        self.killed = _OrderedStats(_KillStats)

    def send_stats(
            self, killtype=None, attackername=None,
            headshot=None, weapon=None, distance=None, health=None):
        """Send victim stats to the player."""
        # Is the player a bot?
        if self.is_fake_client():
            return

        # Get the player's setting
        setting = int(player_dictionary.type_setting.get_setting(self.index))

        # Should hitgroups be included?
        use_hitgroups = setting in (1, 3)

        # Should the stats be printed to chat?
        if setting in (1, 2):

            # Send the player's stats to their chat
            self._send_chat_stats(
                killtype, attackername, headshot,
                weapon, distance, health, use_hitgroups)

        # Should the basic menu be used?
        elif setting in (3, 4):

            # Send the player's stats with a basic menu
            self._send_menu_stats(
                killtype, attackername, headshot,
                weapon, distance, health, use_hitgroups)

        # Should the interactive menu be used?
        elif setting == 5:

            # Send the player's stats using an interactive menu
            self._send_interactive_menu(
                killtype, attackername, headshot,
                weapon, distance, health)

    def _get_hitgroups(self, group):
        """Return a string for the given group's hitgroups."""
        hitgroups = list()
        for hitgroup in group.hitgroups:
            hitgroups.append('{0}: {1}'.format(
                hitgroup_strings[str(hitgroup)].get_string(self.language),
                group.hitgroups[hitgroup]))
        return '; '.join(hitgroups)

    @staticmethod
    def _get_distance(distance):
        return int(distance)


class _OrderedStats(OrderedDict):

    """Class used to store stats in the order they first occur."""

    def __init__(self, default_class):
        """Store the default class to use."""
        super(_OrderedStats, self).__init__()
        self._default_class = default_class

    def __missing__(self, item):
        """Set the given username to an instance of the default class."""
        value = self[item] = self._default_class()
        return value


class _DamageStats(object):

    """Stores damage based stats."""

    def __init__(self):
        """Create the base attributes."""
        self.hits = 0
        self.damage = 0
        self.hitgroups = defaultdict(int)


class _KillStats(object):

    """Stores kills based stats."""

    def __init__(self):
        """Create the base attributes."""
        self.killed = 0
        self.weapon = None
        self.headshot = False
        self.distance = None
