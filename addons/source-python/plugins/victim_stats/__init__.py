# ../victim_stats/__init__.py

"""Verifies the engine is supported and retrieves the translations."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python
from core import SOURCE_ENGINE
from paths import TRANSLATION_PATH
from translations.strings import LangStrings

# Plugin
from .info import info


# =============================================================================
# >> SUPPORT VERIFICATION
# =============================================================================
# Verify that the engine is supported
if not TRANSLATION_PATH.joinpath(
    info.name,
    '{engine}.ini'.format(engine=SOURCE_ENGINE)
).isfile():
    raise NotImplementedError(
        'Engine "{engine}" not supported'.format(engine=SOURCE_ENGINE)
    )


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
# Get the translations
victim_stats_strings = LangStrings('{name}/strings'.format(name=info.name))

# Merge in the engine specific translations
victim_stats_strings.update(
    LangStrings(
        '{name}/{engine}'.format(
            name=info.name,
            engine=SOURCE_ENGINE,
        )
    )
)

# Get the hitgroup translations
hitgroup_strings = LangStrings('{name}/hitgroups'.format(name=info.name))
