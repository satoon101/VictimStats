# ../victim_stats/players.py

"""Stores and interacts with players."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python
from collections import defaultdict

# Source.Python
from menus import SimpleMenu, SimpleOption
from messages import SayText2
from players.entity import Player
from players.helpers import index_from_userid
from settings.player import PlayerSettings

# Plugin
from .colors import ATTACKER_COLOR, KILLED_COLOR, KILLER_COLOR, WOUNDED_COLOR
from .config import (
    display_type, display_type_options, distance_type, distance_type_options,
)
from .info import info
from .strings import CONFIG_STRINGS, TRANSLATION_STRINGS


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
# Create the user settings
user_settings = PlayerSettings(
    name=info.name,
    prefix='vs',
    text=CONFIG_STRINGS['Title'],
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
            text=CONFIG_STRINGS['Menu:default_display_type'],
        )

        # Loop through and add all available options
        for item in display_type_options:
            self.display_type_setting.add_option(
                name=item.split(':')[1],
                text=CONFIG_STRINGS[item],
            )

        self.distance_type_setting = user_settings.add_string_setting(
            name='Distance Type',
            default=str(distance_type.get_int()),
            text=CONFIG_STRINGS['Menu:default_distance_type']
        )

        # Loop through and add all available options
        for item in distance_type_options:
            self.distance_type_setting.add_option(
                name=item.split(':')[1],
                text=CONFIG_STRINGS[item],
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
        self.taken = defaultdict(PlayerDamage)
        self.given = defaultdict(PlayerDamage)
        self.killed = defaultdict(PlayerKill)

    def send_stats(
        self, kill_type=None, attacker_name=None, headshot=None, weapon=None,
        distance=None, health=None
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
                attacker_headshot=headshot,
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
                attacker_headshot=headshot,
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
                attacker_headshot=headshot,
                weapon=weapon,
                distance=distance,
                health=health,
                distance_setting=distance_setting,
            )

    def get_hitgroups(self, group):
        """Return a string for the given group's hitgroups."""
        hitgroups = list()
        for hitgroup, value in group.hitgroups.items():
            hitgroups.append(
                '{name}: {value}'.format(
                    name=TRANSLATION_STRINGS[f'Hitgroup:{hitgroup}'].get_string(self.language),
                    value=value,
                )
            )
        return ' - ' + '; '.join(hitgroups)

    def get_weapon_info(self, string_name, kill_info, distance_setting, for_menu=False):
        """"""
        if string_name not in ('Killed', 'Killer'):
            return '', ''

        if kill_info is None:
            return '', ''

        return TRANSLATION_STRINGS['Base:Weapon'].get_string(
            language=self.language,
            weapon_color='' if for_menu else '\x05',
            weapon=kill_info.weapon,
            at_color='' if for_menu else '\x01',
            distance_color='' if for_menu else '\x04',
            distance=self.get_distance_display(kill_info.distance, distance_setting),
        ), TRANSLATION_STRINGS['Headshot'] if kill_info.headshot and not for_menu else ''

    def iter_messages(self, string_name, group, use_hitgroups, distance_setting, color=None):
        """"""
        for_menu = color is None
        for username, values in group.items():
            hitgroups = self.get_hitgroups(values) if use_hitgroups else ''
            weapon_info, headshot = self.get_weapon_info(string_name, self.killed.get(username), distance_setting, for_menu)
            yield TRANSLATION_STRINGS['Base'].get_string(
                self.language,
                type_color=color or '',
                type=TRANSLATION_STRINGS[f'Type:{string_name}'] if not for_menu else '',
                name_color='' if for_menu else '\x04',
                name=username,
                damage_color='' if for_menu else '\x01',
                damage=group[username].damage,
                weapon_info=weapon_info,
                headshot=headshot,
                hitgroup_info=hitgroups,
            )

    def get_kill_message(self, kill_type, attacker_name, attacker_headshot, weapon, distance, health, distance_setting, color=None):
        """"""
        if kill_type is None:
            return None

        if kill_type in ('Suicide', 'Team Killed'):
            return TRANSLATION_STRINGS[kill_type].get_string(name=attacker_name)

        for_menu = color is None
        weapon_info, headshot = self.get_weapon_info('Killer', PlayerKill(weapon, attacker_headshot, distance), distance_setting, for_menu)
        return TRANSLATION_STRINGS['Killer' if health else 'Killer:Dead'].get_string(
            self.language,
            type_color='' if for_menu else color,
            headshot=headshot,
            name_color='' if for_menu else '\x04',
            name=attacker_name,
            weapon_info=weapon_info,
            health=health,
        )

    def send_chat_stats(
        self, kill_type, attacker_name, attacker_headshot, weapon, distance,
        health, distance_setting, use_hitgroups
    ):
        """Send victim stats to the player's chat."""
        wounded_only = {
            username: values
            for username, values in self.given.items()
            if username not in self.killed
        }
        killed_only = {
            username: values
            for username, values in self.given.items()
            if username in self.killed
        }
        for string_name, group, color in (
            ('Attacker', self.taken, ATTACKER_COLOR),
            ('Wounded', wounded_only, WOUNDED_COLOR),
            ('Killed', killed_only, KILLED_COLOR),
        ):
            for message in self.iter_messages(string_name, group, use_hitgroups, distance_setting, color):
                SayText2(message=message).send(self.index)

        kill_message = self.get_kill_message(kill_type, attacker_name, attacker_headshot, weapon, distance, health, distance_setting, KILLER_COLOR)
        if kill_message is not None:
            SayText2(message=kill_message).send(self.index)

    def send_menu_stats(
        self, kill_type, attacker_name, attacker_headshot, weapon, distance,
        health, distance_setting, use_hitgroups
    ):
        """Send victim stats to the player via a menu."""
        wounded_only = {
            username: values
            for username, values in self.given.items()
            if username not in self.killed
        }
        killed_only = {
            username: values
            for username, values in self.given.items()
            if username in self.killed
        }
        menu = SimpleMenu()
        for num, (string_name, group) in enumerate(
            iterable=[
                ('Attackers', self.taken),
                ('Wounded', wounded_only),
                ('Killed', killed_only),
            ],
            start=1
        ):
            if not group:
                continue

            menu.append(SimpleOption(num, TRANSLATION_STRINGS[f'Type:{string_name}'], selectable=False))
            for message in self.iter_messages(string_name, group, use_hitgroups, distance_setting):
                menu.append('  ' + message)

        kill_message = self.get_kill_message(kill_type, attacker_name, attacker_headshot, weapon, distance, health, distance_setting)
        if kill_message:
            menu.append(SimpleOption(4, TRANSLATION_STRINGS['Type:Killer'], selectable=False))
            menu.append('   ' + kill_message)

        menu.send(self.index)

    def send_interactive_menu(
        self, kill_type, attacker_name, attacker_headshot, weapon, distance,
        health, distance_setting
    ):
        """Send victim stats to the player via an interactive menu."""
        pass

    @staticmethod
    def get_distance_display(distance, setting):
        """Return the formatted distance between players."""
        feet = distance * 0.0375
        if setting == 1:
            return '{feet:.2f}ft'.format(feet=feet)
        meters = feet * 0.3408
        if setting == 0:
            return '{meters:.2f}m'.format(meters=meters)
        return '{meters:.2f}m ({feet:.2f}ft)'.format(meters=meters, feet=feet)


class PlayerDamage(object):
    """"""

    def __init__(self):
        """"""
        self.damage = 0
        self.hits = 0
        self.hitgroups = defaultdict(int)


class PlayerKill(object):
    """"""

    def __init__(self, weapon=None, headshot=False, distance=0):
        """"""
        self.kills = 0
        self.weapon = weapon
        self.headshot = headshot
        self.distance = distance
