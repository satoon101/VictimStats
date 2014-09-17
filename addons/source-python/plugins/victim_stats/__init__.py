# ../victim_stats/__init__.py

"""Verifies the engine is supported and retrieves the translations."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Core
from core import SOURCE_ENGINE
#   Paths
from paths import TRANSLATION_PATH
#   Translations
from translations.strings import LangStrings

# Script Imports
from victim_stats.info import info


# =============================================================================
# >> SUPPORT VERIFICATION
# =============================================================================
# Verify that the engine is supported
if not TRANSLATION_PATH.joinpath(
        info.basename, '{0}.ini'.format(SOURCE_ENGINE)).isfile():
    raise NotImplementedError(
        'Engine "{0}" not supported'.format(SOURCE_ENGINE))


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
# Get the translations
victim_stats_strings = LangStrings('{0}/strings'.format(info.basename))

# Merge in the engine specific translations
victim_stats_strings.update(
    LangStrings('{0}/{1}'.format(info.basename, SOURCE_ENGINE)))

# Get the hitgroup translations
hitgroup_strings = LangStrings('{0}/hitgroups'.format(info.basename))
