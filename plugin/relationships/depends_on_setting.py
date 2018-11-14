from cloudify import ctx
from cloudify.state import ctx_parameters as inputs
from cloudify.decorators import operation
from cloudify.exceptions import *

def reset_log_indentation():
    ctx.source.instance.runtime_properties['indent'] = 0

def get_log_indentation():
    if 'indent' in ctx.source.instance.runtime_properties:
        return '\t'*ctx.source.instance.runtime_properties['indent']
    else:
        return ''

def increase_log_indentation():
    ctx.source.instance.runtime_properties['indent'] += 1

def decrease_log_indentation():
    ctx.source.instance.runtime_properties['indent'] -= 1

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

@operation
def preconfigure(config, simulate, **kwargs):
    if (not simulate):
        reset_log_indentation()
        ctx.logger.debug('{0} Preconfigure operation: Begin'.format(get_log_indentation()))
        increase_log_indentation()
        target_radl = get_child(dictionary=ctx.target.instance.runtime_properties, key='settings', required=True)
        ctx.logger.debug('{0} RADL: {1}'.format(get_log_indentation(), str(target_radl)))
        if target_radl:
            source_radl = get_child(ctx.source.instance.runtime_properties, key='settings')
            if not source_radl or not isinstance(source_radl, dict):
                source_radl = create_child(ctx.source.instance.runtime_properties, key='settings', value={})
            ctx.logger.debug('{0} Copy partial RADL from target to source:'.format(get_log_indentation()))
            increase_log_indentation()
            for key in target_radl:
                partial_source_radl = create_child(source_radl, key=key, value=target_radl[key])
            decrease_log_indentation()
        decrease_log_indentation()
        ctx.logger.debug('{0} Preconfigure operation: End'.format(get_log_indentation()))
    

