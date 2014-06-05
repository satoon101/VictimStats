# ../victim_stats/victim_stats.py

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Config
from config.manager import ConfigManager
#   Settings
from settings.player import PlayerSettings
#   Translations
from translations.strings import LangStrings

# Script Imports
from victim_stats.info import info


# =============================================================================
# >> PUBLIC VARIABLE
# =============================================================================
# Make sure the variable is set to the proper version
info.convar.set_string(info.version)

# Make the variable public
info.convar.make_public()


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
# Get the translations
victim_stats_strings = LangStrings('victim_stats')


class _VictimStats(dict):
    def __missing__(self, userid):
        value = self[userid] = _PlayerStats(userid)
        return value

    def __delitem__(self, userid):
        if userid in self:
            super(_VictimStats, self).__delitem__(userid)

VictimStats = _VictimStats()


class _PlayerStats(PlayerEntity):
    def __new__(cls, userid):
        self = super(_PlayerStats, cls).__new__(cls, index_from_userid(userid))
        return self

    def __init__(self, userid):
        self.taken = _DamageDictionary()
        self.given = _DamageDictionary()
        self.kills = _KillsDictionary()

    def send_stats(
            self, killtype=None, attackername=None,
            headshot=None, weapon=None, distance=None, health=None):

        if self.is_fake_client():
            return

        setting = VictimStats.location.get_setting(self.index)
        if not setting in range(1, 6):
            return
        if setting in (1, 2):
            self._sent_chat_stats(
                killtype, attackername, headshot,
                weapon, distance, health, setting == 1)

        elif setting in (3, 4):
            self._send_gui_stats(
                killtype, attackername, headshot,
                weapon, distance, health, setting == 3)
        elif setting == 5:
            self._send_gui_menu(
                killtype, attackername, headshot,
                weapon, distance, health)

    def _send_chat_stats(
            killtype, attackername. headshot,
            weapon, distance, health, use_hitgroups):

        pass

    def _send_gui_stats(
            killtype, attackername. headshot,
            weapon, distance, health, use_hitgroups):

        pass

    def _send_gui_menu(
            killtype, attackername. headshot,
            weapon, distance, health):

        pass


class _Damage(object):
    def __init__(self):
        self.hits = 0
        self.damage = 0
        self.hitgroups = _HitGroups()


class _Kills(object):
    def __init__(self):
        self.kills = 0
        self.weapon = None
        self.headshot = False
        self.distance = None


class _StatsDictionary(dict):
    def __missing__(self, username):
        value = self[username] = self.instance()
        return value

class _DamageDictionary(_StatsDictionary):
    instance = _Damage


class _KillsDictionary(dict):
    instance = _Kills


class _HitGroups(dict):
    def __missing__(self, hitgroup):
        value = self[hitgroup] = 0
        return value


@Event
def player_hurt(game_event):
    attacker = _get_valid_attacker(game_event)
    if not isinstance(attacker, _PlayerStats):
        return
    victim = VictimStats[game_event.get_int('userid')]
    damage = game_event.get_int('dmg_health')
    hitgroup = game_event.get_int('hitgroup')
    if victim.name in attacker.kills:
        given = attacker.kills[victim.name]
    else:
        given = attacker.given[victim.name]
    taken = victim.taken[attacker.name]
    given.damage += damage
    given.hits += 1
    given.hitgroups[hitgroup] += 1
    taken.damage += damage
    taken.hits += 1
    taken.hitgroups[hitgroup] += 1


@Event
def player_death(game_event):
    attacker = _get_valid_attacker(game_event)
    victim = VictimStats[game_event.get_int('userid')]
    if isinstance(attacker, _PlayerStats):

        headshot = game_event.get_bool('headshot')
        weapon = game_event.get_string('weapon')
        distance = attacker.m_vecOrigin.get_distance(victim.m_vecOrigin)

        kills = attacker.kills[victim.name]
        kills.kills += 1
        kills.headshot = headshot
        kills.weapon = weapon
        kills.distance = distance

        victim.send_stats(
            'Killer', attacker.name, headshot, weapon,
            distance, game_event.get_int('health'))

        return

    if attacker is None:

        victim.send_stats('Suicide')

    else:

        victim.send_stats('Team-Killed')


@Event
def round_end(game_event):
    for userid in PlayerIter('alive', return_types='userid'):
        VictimStats[userid].send_stats()


def _get_valid_attacker(game_event):
    '''Returns the attacker's userid if not a self or team inflicted event'''

    # Get the attacker's userid
    attacker = game_event.get_int('attacker')

    # Get the victim's userid
    victim = game_event.get_int('userid')

    # Was this self inflicted?
    if attacker in (victim, 0):

        # If self, inflicted, do not count
        return None

    # Get the victim's PlayerInfo instance
    vplayer = playerinfo_from_userid(victim)

    # Get the attacker's PlayerInfo instance
    aplayer = playerinfo_from_userid(attacker)

    # Are the player's on the same team?
    if vplayer.get_team_index() == aplayer.get_team_index():

        # Do not count
        return index_from_playerinfo(aplayer)

    # If all checks pass, count the attack/kill
    return VictimStats[attacker]
