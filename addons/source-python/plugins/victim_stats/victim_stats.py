# ../victim_stats/victim_stats.py

"""Stores victim stat information and displays it on player death."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Events
from events import Event
#   Filters
from filters.players import PlayerIter
#   Players
from players.helpers import index_from_playerinfo
from players.helpers import playerinfo_from_userid

# Script Imports
from victim_stats.players import PlayerStats
from victim_stats.players import player_dictionary


# =============================================================================
# >> GAME EVENTS
# =============================================================================
@Event
def player_hurt(game_event):
    """Add the stats for the given attack."""
    # Get the attacker
    attacker = _get_valid_attacker(game_event)

    # Should the victim stats be collected?
    if not isinstance(attacker, PlayerStats):
        return

    # Get the victim
    victim = player_dictionary[game_event.get_int('userid')]

    # Get the damage
    damage = game_event.get_int('dmg_health')

    # Get the hitgroup that was hit
    hitgroup = game_event.get_int('hitgroup')

    # Add the damage stats to the attacker's dictionary for the victim
    given = attacker.given[victim.name]
    given.damage += damage
    given.hits += 1
    given.hitgroups[hitgroup] += 1

    # Add the damage stats to the victim's dictionary for the attacker
    taken = victim.taken[attacker.name]
    taken.damage += damage
    taken.hits += 1
    taken.hitgroups[hitgroup] += 1


@Event
def player_death(game_event):
    """Send victim their stats and add the victim to the attacker's kills."""
    # Get the attacker
    attacker = _get_valid_attacker(game_event)

    # Get the victim
    victim = player_dictionary[game_event.get_int('userid')]

    # Was this a good kill (non-team/non-suicide)?
    if isinstance(attacker, PlayerStats):

        # Get whether this kill was a headshot
        headshot = game_event.get_bool('headshot')

        # Get the killing weapon
        weapon = game_event.get_string('weapon')

        # Get the distance from the attacker to the victim
        distance = attacker.get_key_value_vector(
            'origin').get_distance(victim.get_key_value_vector('origin'))

        # Add the kill stats to the attacker's dictionary for the victim
        kills = attacker.killed[victim.name]
        kills.killed += 1
        kills.headshot = headshot
        kills.weapon = weapon
        kills.distance = distance

        # Send the victim their victim stats
        victim.send_stats(
            'Killer Alive' if attacker.health > 0 else 'Killer Dead',
            attacker.name, headshot, weapon, distance, attacker.health)

    # Was this a suicide?
    elif attacker is None:

        # Send the victim their victim stats with suicide message
        victim.send_stats('Suicide')

    # Was this a team-kill?
    else:

        # Send the victim their victim stats with team-kill message
        victim.send_stats('Team-Killed', attacker.name)


@Event
def player_spawn(game_event):
    """Remove the player's stats when they spawn."""
    del player_dictionary[game_event.get_int('userid')]


@Event
def round_start(game_event):
    """Clear the player dictionary."""
    player_dictionary.clear()


@Event
def round_end(game_event):
    """Send stats to players who survived the round."""
    # Is the game commencing?
    if game_event.get_int('reason') == 15:
        return

    # Loop through all living players
    for userid in PlayerIter('alive', 'bot', 'userid'):

        # Send the player their stats
        player_dictionary[userid].send_stats()


# =============================================================================
# >> HELPER FUNCTIONS
# =============================================================================
def _get_valid_attacker(game_event):
    """Return the attacker's userid if not a self or team inflicted event."""
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
    return player_dictionary[attacker]
