# ../victim_stats/players.py

"""Stores and interacts with players."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python
from collections import defaultdict
from functools import partial
from warnings import warn

# Source.Python
import colors
from filters.players import PlayerIter
from messages import SayText2
from players.entity import Player
from players.helpers import index_from_userid
from settings.player import PlayerSettings

# Plugin
from . import hitgroup_strings, victim_stats_strings
from .config import (
    attacker_color, display_type, display_type_options, distance_type,
    distance_type_options, killed_color, killer_color, wounded_color,
)
from .info import info


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
# Create the user settings
user_settings = PlayerSettings(
    name=info.name,
    prefix='vs',
    text=victim_stats_strings['Title'],
)

damage_stats = partial(
    dict,
    hits=0,
    damage=0,
    hitgroups=defaultdict(int),
)
kill_stats = partial(
    dict,
    kills=0,
    weapon=None,
    headshot=False,
    distance=None,
)


# =============================================================================
# >> CLASSES
# =============================================================================
class _PlayerDictionary(dict):

    """Stores players with their victim stats information."""

    def __init__(self):
        """Create the user setting and store its options."""
        # Call the super class' init
        super(_PlayerDictionary, self).__init__()

        # Create the setting
        self.display_type_setting = user_settings.add_string_setting(
            name='Display Type',
            default=str(display_type.get_int()),
            text=victim_stats_strings['Menu:default_display_type'],
        )

        # Loop through and add all available options
        for item in display_type_options:
            self.display_type_setting.add_option(
                name=item.split(':')[1],
                text=victim_stats_strings[item],
            )

        self.distance_type_setting = user_settings.add_string_setting(
            name='Distance Type',
            default=str(distance_type.get_int()),
            text=victim_stats_strings['Menu:default_distance_type']
        )

        # Loop through and add all available options
        for item in distance_type_options:
            self.distance_type_setting.add_option(
                name=item.split(':')[1],
                text=victim_stats_strings[item],
            )

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


class PlayerStats(Player):

    """Store victim stats information and display it when the player dies."""

    def __init__(self, index):
        """Create the base dictionaries to store victim stats information."""
        super().__init__(index)
        self.taken = defaultdict(damage_stats)
        self.given = defaultdict(damage_stats)
        self.killed = defaultdict(kill_stats)

    def send_stats(
        self, kill_type=None, attacker_name=None,
        headshot=None, weapon=None, distance=None, health=None
    ):
        """Send victim stats to the player."""
        # Is the player a bot?
        if self.is_fake_client():
            return

        # Get the player's settings
        setting = int(
            player_dictionary.display_type_setting.get_setting(self.index)
        )
        distance_setting = int(
            player_dictionary.distance_type_setting.get_setting(self.index)
        )

        # Should hitgroups be included?
        use_hitgroups = setting in (1, 3)

        # Should the stats be printed to chat?
        if setting in (1, 2):
            self.send_chat_stats(
                kill_type=kill_type,
                attacker_name=attacker_name,
                headshot=headshot,
                weapon=weapon,
                distance=distance,
                health=health,
                distance_setting=distance_setting,
                use_hitgroups=use_hitgroups,
            )

        # Should the basic menu be used?
        elif setting in (3, 4):
            self.send_menu_stats(
                kill_type=kill_type,
                attacker_name=attacker_name,
                headshot=headshot,
                weapon=weapon,
                distance=distance,
                health=health,
                distance_setting=distance_setting,
                use_hitgroups=use_hitgroups,
            )

        # Should the interactive menu be used?
        elif setting == 5:
            self.send_interactive_menu(
                kill_type=kill_type,
                attacker_name=attacker_name,
                headshot=headshot,
                weapon=weapon,
                distance=distance,
                health=health,
                distance_setting=distance_setting,
            )

    def get_hitgroups(self, group):
        """Return a string for the given group's hitgroups."""
        hitgroups = list()
        for hitgroup in group['hitgroups']:
            current = str(hitgroup)
            hitgroups.append(
                '{name}: {value}'.format(
                    name=hitgroup_strings[current].get_string(self.language),
                    value=group['hitgroups'][hitgroup],
                )
            )
        return '; '.join(hitgroups)

    @staticmethod
    def get_distance_display(distance, setting):
        """Return the formatted distance between players."""
        feet = distance * 0.0375
        if setting == 0:
            return '{feet:.2f}ft'.format(feet=feet)
        meters = feet * 0.3408
        if setting == 1:
            return '{meters:.2f}m'.format(meters=meters)
        return '{meters:.2f}m ({feet:.2f}ft)'.format(meters=meters, feet=feet)

    def send_chat_stats(
        self, kill_type, attacker_name, headshot, weapon, distance, health,
        distance_setting, use_hitgroups
    ):
        """Send victim stats to the player's chat."""
        index = self.get_opposing_index()
        wounded_only = {
            username: values
            for username, values in self.given.items()
            if username not in self.killed
        }
        for string_name, group, cvar in (
            ('Attacker', self.taken, attacker_color),
            ('Wounded', wounded_only, wounded_color),
        ):
            string_name = 'Chat {name} '.format(name=string_name)
            string_name += '{key} Hitgroups' if use_hitgroups else '{key}'
            color = self.get_color(cvar)
            for username in group:
                values = group[username]
                current_string = string_name.format(
                    key='Single' if values['hits'] == 1 else 'Multi'
                )
                hitgroups = self.get_hitgroups(values) if use_hitgroups else ''
                SayText2(
                    message=victim_stats_strings[current_string],
                    index=index,
                ).send(
                    self.index,
                    color=color,
                    name=username,
                    damage=group[username]['damage'],
                    hits=group[username]['hits'],
                    hitgroups=hitgroups,
                )

        color = self.get_color(killed_color)
        string_name = 'Chat Killed {key}'
        string_name += ' Hitgroups' if use_hitgroups else ''
        for username in self.killed:
            if username not in self.given:
                continue
            kills = self.killed[username]
            given = self.given[username]
            if kills['kills'] > 1:
                SayText2(
                    message=victim_stats_strings['Chat Multi Kills'],
                    index=index,
                ).send(
                    self.index,
                    color=color,
                    name=username,
                    damage=given['damage'],
                    kills=kills['kills'],
                )
            else:
                current_string = string_name.format(
                    key='Single' if given['hits'] == 1 else 'Multi'
                )
                kill_headshot = ' HS' if kills['headshot'] else ''
                hitgroups = self.get_hitgroups(given) if use_hitgroups else ''
                kill_distance = self.get_distance_display(
                    distance=kills['distance'],
                    setting=distance_setting,
                )
                SayText2(
                    message=victim_stats_strings[current_string],
                    index=index,
                ).send(
                    self.index,
                    color=color,
                    headshot=kill_headshot,
                    name=username,
                    damage=given['damage'],
                    hits=given['hits'],
                    weapon=kills['weapon'],
                    distance=kill_distance,
                    hitgroups=hitgroups,
                )

        if kill_type is None:
            return

        if kill_type in ('Suicide', 'Team Killed'):
            SayText2(
                message=victim_stats_strings[kill_type]
            ).send(
                self.index,
                name=attacker_name,
            )
            return

        color = self.get_color(killer_color)
        headshot = ' HS' if headshot else ''
        distance = self.get_distance_display(
            distance=distance,
            setting=distance_setting,
        )
        SayText2(
            message=(
                victim_stats_strings[
                    'Chat {kill_type}'.format(
                        kill_type=kill_type
                    )
                ]
            ),
            index=index,
        ).send(
            self.index,
            color=color,
            headshot=headshot,
            name=attacker_name,
            weapon=weapon,
            distance=distance,
            health=health,
        )

    def get_opposing_index(self):
        """Return an index from the opposing team."""
        for player in PlayerIter():
            if player.team == 5 - self.team:
                return player.index
        return 0

    @staticmethod
    def get_color(cvar):
        """Return the color for the given cvar."""
        if cvar is None:
            return None
        value = cvar.get_string()
        if value in colors.__all__:
            return getattr(colors, value)
        try:
            red, green, blue = map(int, value.split(','))
            return colors.Color(red, green, blue)
        except ValueError:
            warn(
                'Cvar "{cvar}" not set to a proper value.'.format(
                    cvar=cvar.get_name() + '  Returning RED instead.',
                )
            )
            return colors.RED

    def send_menu_stats(
        self, kill_type, attacker_name, headshot, weapon, distance, health,
        distance_setting, use_hitgroups
    ):
        """Send victim stats to the player via a menu."""
        pass

    def send_interactive_menu(
        self, kill_type, attacker_name, headshot, weapon, distance, health,
        distance_setting
    ):
        """Send victim stats to the player via an interactive menu."""
        pass
