# ../victim_stats/info.py

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Plugins
from plugins.info import PluginInfo


# =============================================================================
# >> PLUGIN INFO
# =============================================================================
info = PluginInfo()
info.name = 'Victim Stats'
info.author = 'Satoon101'
info.version = '1.0'
info.basename = 'victim_stats'
info.variable = info.basename + '_version'
info.url = ''
info.convar = ServerVar(info.variable, info.version, 0, info.name + ' Version')
