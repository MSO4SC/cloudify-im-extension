from cloudify import ctx
from cloudify.state import ctx_parameters as inputs
from cloudify.decorators import operation
from cloudify.exceptions import *
from plugin.nodes.utils import *

def build_radl_network(config):
    ctx.logger.debug('{0} Infrastructure Manager deployment info:'.format(get_log_indentation()))
    increase_log_indentation()

    outbound = get_child(dictionary=config, key='outbound', required=True)

    outbound_str = 'yes'
    if not outbound:
        outbound_str = 'no'

    network_radl = \
"network  net  ( \n" + \
"    outbound = '" + outbound_str + "' \n" + \
")\n" 
    decrease_log_indentation()
    return network_radl

@operation
def configure(config, simulate, **kwargs):
    if (not simulate):
        reset_log_indentation()
        ctx.logger.debug('{0} Configure operation: Begin'.format(get_log_indentation()))
        increase_log_indentation()
        radl = get_child(ctx.instance.runtime_properties, key='settings')
        if not radl:
            radl = create_child(ctx.instance.runtime_properties, key='settings', value={})
        radl_network = create_child(radl, key='network', value=build_radl_network(config))
        decrease_log_indentation()
        ctx.logger.debug('{0} Configure operation: End'.format(get_log_indentation()))


