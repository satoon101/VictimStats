# ../victim_stats/menu.py

"""Provides methods for sending menu based victim stats messages."""


# =============================================================================
# >> CLASSES
# =============================================================================
class _MenuStats(object):

    """Class used to send menu based victim stats messages."""

    def _send_menu_stats(
            self, killtype, attackername, headshot,
            weapon, distance, health, use_hitgroups):
        """Send victim stats to the player via a menu."""
        pass

    def _send_interactive_menu(
            self, killtype, attackername, headshot,
            weapon, distance, health):
        """Send victim stats to the player via an interactive menu."""
        pass
