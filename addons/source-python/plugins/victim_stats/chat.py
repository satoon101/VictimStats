# ../victim_stats/chat.py

"""Provides methods for sending chat victim stats messages."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
#   Warnings
from warnings import warn

# Source.Python Imports
#   Basetypes
from basetypes import Color
#   Colors
import colors
#   Filters
from filters.players import PlayerIter
#   Messages
from messages import SayText

# Script Imports
from victim_stats import victim_stats_strings
from victim_stats.config import attacker_color
from victim_stats.config import killed_color
from victim_stats.config import killer_color
from victim_stats.config import wounded_color


# =============================================================================
# >> CLASSES
# =============================================================================
class _ChatStats(object):

    """Class used to send chat victim stats messages."""

    def _send_chat_stats(
            self, killtype, attackername, headshot,
            weapon, distance, health, use_hitgroups):
        """Send victim stats to the player's chat."""
        index = self._get_opposing_index()
        wounded_only = {
            username: values for username, values in
            self.given.items() if username not in self.killed}
        for string_name, group, cvar in (
                ('Attacker', self.taken, attacker_color),
                ('Wounded', wounded_only, wounded_color)):
            string_name = 'Chat {0} '.format(string_name)
            string_name += '{0} Hitgroups' if use_hitgroups else '{0}'
            color = self._get_color(cvar)
            for username in group:
                values = group[username]
                current_string = string_name.format(
                    'Single' if values.hits == 1 else 'Multi')
                hitgroups = self._get_hitgroups(
                    values) if use_hitgroups else ''
                SayText(message=victim_stats_strings[
                    current_string], index=index).send(
                        self.index, color=color, name=username,
                        damage=group[username].damage,
                        hits=group[username].hits, hitgroups=hitgroups)

        color = self._get_color(killed_color)
        string_name = 'Chat Killed {0}'
        string_name += ' Hitgroups' if use_hitgroups else ''
        for username in self.killed:
            if username not in self.given:
                continue
            kills = self.killed[username]
            given = self.given[username]
            if kills.killed > 1:
                SayText(message=victim_stats_strings[
                    'Chat Multi Kills'], index=index).send(
                        self.index, color=color, name=username,
                        damage=given.damage, kills=kills.kills)
            else:
                current_string = string_name.format(
                    'Single' if given.hits == 1 else 'Multi')
                _headshot = ' HS' if kills.headshot else ''
                hitgroups = self._get_hitgroups(
                    given) if use_hitgroups else ''
                _distance = self._get_distance(kills.distance)
                SayText(message=victim_stats_strings[
                    current_string], index=index).send(
                        self.index, color=color, headshot=_headshot,
                        name=username, damage=given.damage, hits=given.hits,
                        weapon=kills.weapon, distance=_distance,
                        hitgroups=hitgroups)

        if killtype is None:
            return

        if killtype in ('Suicide', 'Team Killed'):
            SayText(message=victim_stats_strings[killtype]).send(
                self.index, name=attackername)
            return

        color = self._get_color(killer_color)
        _headshot = ' HS' if headshot else ''
        _distance = self._get_distance(distance)
        SayText(message=victim_stats_strings[
            'Chat {0}'.format(killtype)], index=index).send(
                self.index, color=color, headshot=_headshot, name=attackername,
                weapon=weapon, distance=_distance, health=health)

    def _get_opposing_index(self):
        """Return an index from the opposing team."""
        for player in PlayerIter(return_types='player'):
            if player.team == 5 - self.team:
                return player.index
        return 0

    def _get_chat_message(self, string, color, **tokens):
        """"""
        message = victim_stats_strings[string].get_string(self.index, **tokens)
        if color is not None and '{0}' in message:
            message = message.format(color)
        return message

    @staticmethod
    def _get_color(cvar):
        """Return the color for the given cvar."""
        if cvar is None:
            return None
        value = cvar.get_string()
        if value in colors.__all__:
            return getattr(colors, value)
        try:
            red, green, blue = map(int, value.split(','))
            return Color(red, green, blue)
        except ValueError:
            warn(
                'Cvar "{0}" not set to a proper value.'.format(
                    cvar.get_name() + '  Returning RED instead.'))
            return colors.RED
