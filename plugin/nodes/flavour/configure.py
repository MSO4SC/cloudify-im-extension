from cloudify import ctx
from cloudify.state import ctx_parameters as inputs
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


def build_radl_flavour():
    ctx.logger.debug('{0} Infrastructure Manager deployment info:'.format(get_log_indentation()))
    increase_log_indentation()

    config   = get_child(dictionary=inputs, key='config', required=True)
    type = get_child(dictionary=config, key='type', required=True)
    cores = get_child(dictionary=config, key='cores', required=True)
    memory = get_child(dictionary=config, key='memory', required=True)

    flavour_radl = \
"    instance_type = '" + str(type) + "' and \n" + \
"    cpu.count = " + str(cores) + " and \n" + \
"    memory.size = " + str(memory) + " and \n"

    decrease_log_indentation()
    return flavour_radl


def configure():
    reset_log_indentation()
    ctx.logger.debug('{0} Configure operation: Begin'.format(get_log_indentation()))
    increase_log_indentation()
    radl = get_child(ctx.instance.runtime_properties, key='settings')
    if not radl:
        radl = create_child(ctx.instance.runtime_properties, key='settings', value={})
    radl_network = create_child(radl, key='flavour', value=build_radl_flavour())
    decrease_log_indentation()
    ctx.logger.debug('{0} Configure operation: End'.format(get_log_indentation()))

#    ctx.logger.info('Create server')
#    ctx.logger.info('Just logging the node instance: {0}'
#                    .format(str(ctx.instance)))
#    ctx.logger.info('Just logging the runtime properties: {0}'
#                    .format(str(ctx.instance.runtime_properties)))
#    ctx.logger.info('The config operation input is : {0}'
#                    .format(str(inputs)))

    
if (not get_child(dictionary=inputs, key='simulate', required=False)):
    configure()
