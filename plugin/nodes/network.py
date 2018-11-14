from cloudify import ctx
from cloudify.state import ctx_parameters as inputs
from cloudify.decorators import operation
from cloudify.exceptions import *

def reset_log_indentation():
    ctx.instance.runtime_properties['indent'] = 0

def get_log_indentation():
    if 'indent' in ctx.instance.runtime_properties:
        return '\t'*ctx.instance.runtime_properties['indent']
    else:
        return ''

def increase_log_indentation():
    ctx.instance.runtime_properties['indent'] += 1

def decrease_log_indentation():
    ctx.instance.runtime_properties['indent'] -= 1

def get_child(dictionary, key, required=False, debug=False):
    child = None
    if key not in dictionary:
        msg = '{0} Required key "{1}" not defined!'.format(get_log_indentation(), str(key))
        if required:
            raise NonRecoverableError(msg)
        else:
            ctx.logger.debug(msg)
    else:
        ctx.logger.debug('{0} Obtaining key "{1}"'.format(get_log_indentation(), str(key)))
        child = dictionary[key]
    return child

def create_child(dictionary, key, value):
    child = get_child(dictionary=dictionary, key=key, required=False)
    if child is None:
        msg = '{0} New key "{1}" defined!'.format(get_log_indentation(), str(key))
        ctx.logger.debug(msg)
        dictionary[key] = value
        child = dictionary[key]
    return child


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
def configure(config, simulate):
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


