import requests
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

def delete():
    reset_log_indentation()
    ctx.logger.debug('{0} Delete operation: Begin'.format(get_log_indentation()))
    increase_log_indentation()
    config = get_child(dictionary=inputs, key='config', required=True)
    host = get_child(dictionary=config, key='host', required=True)
    headers = get_child(dictionary=ctx.instance.runtime_properties, key='headers', required=True)
    infrastructure_id = get_child(dictionary=ctx.instance.runtime_properties, key='infrastructure_id', required=True)
    response = requests.delete(url=infrastructure_id, headers=headers)
    ctx.logger.debug('{0} Response code: {1}'.format(get_log_indentation(), str(response.status_code)))
    ctx.logger.info('{0} Infrastructure ID: {1} deleted!'.format(get_log_indentation(), infrastructure_id))
    response.raise_for_status()
    decrease_log_indentation()
    ctx.logger.debug('{0} Delete operation: End'.format(get_log_indentation()))

if (not get_child(dictionary=inputs, key='simulate', required=False)):
    delete()
