# ../victim_stats/victim_stats.py

"""Stores victim stat information and displays it on player death."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python
from events import Event
from filters.players import PlayerIter

# Plugin
from .players import PlayerStats, player_dictionary


# =============================================================================
# >> GAME EVENTS
# =============================================================================
@Event("player_hurt")
def _player_hurt(game_event):
    """Add the stats for the given attack."""
    # Get the attacker
    attacker, victim = _get_attacker_and_victim(game_event)

    # Should the victim stats be collected?
    if not isinstance(attacker, PlayerStats):
        return

    damage = game_event["dmg_health"]
    hitgroup = game_event["hitgroup"]

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


@Event("player_death")
def _player_death(game_event):
    """Send victim their stats and add the victim to the attacker's kills."""
    attacker, victim = _get_attacker_and_victim(game_event)

    # Was this a good kill (non-team/non-suicide)?
    if isinstance(attacker, PlayerStats):

        headshot = game_event["headshot"]
        weapon = game_event["weapon"]
        distance = attacker.origin.get_distance(victim.origin)

        # Add the kill stats to the attacker's dictionary for the victim
        kills = attacker.killed[victim.name]
        kills.kills += 1
        kills.headshot = headshot
        kills.weapon = weapon
        kills.distance = distance

        # Send the victim their victim stats
        victim.send_stats(
            kill_type="Killer Alive" if attacker.health > 0 else "Killer Dead",
            attacker_name=attacker.name,
            headshot=headshot,
            weapon=weapon,
            distance=distance,
            health=attacker.health,
        )

    # Was this a suicide?
    elif attacker is None:
        victim.send_stats(
            kill_type="Suicide",
        )

    # Was this a team-kill?
    else:
        victim.send_stats(
            kill_type="Team-Killed",
            attacker_name=attacker,
        )


@Event("player_spawn")
def _player_spawn(game_event):
    """Remove the player's stats when they spawn."""
    del player_dictionary[game_event["userid"]]


@Event("round_start")
def _round_start(game_event):
    """Clear the player dictionary."""
    player_dictionary.clear()


@Event("round_end")
def _round_end(game_event):
    """Send stats to players who survived the round."""
    # Is the game commencing?
    if game_event["reason"] == 15:
        return

    # Send all living human players their round stats
    for player in PlayerIter(
        is_filters=["alive"],
        not_filters=["bot"],
    ):
        player_dictionary[player.userid].send_stats()


# =============================================================================
# >> HELPER FUNCTIONS
# =============================================================================
def _get_attacker_and_victim(game_event):
    """Return the attacker's userid if not a self or team inflicted event."""
    attacker = game_event["attacker"]
    victim = game_event["userid"]

    # Was this self inflicted?
    if attacker in (victim, 0):
        return None, None

    victim = player_dictionary[victim]
    attacker = player_dictionary[attacker]

    # Are the player's on the same team?
    if victim.team == attacker.team:
        return attacker.name, victim

    # If all checks pass, count the attack/kill
    return attacker, victim
