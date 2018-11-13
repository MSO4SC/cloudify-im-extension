import time
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

def wait_for_configuration(timestep):
    '''
    
    '''
    increase_log_indentation()
    vm_id = get_child(dictionary=ctx.instance.runtime_properties, key='vm_id', required=True)
    headers = get_child(dictionary=ctx.instance.runtime_properties, key='headers', required=True)
    while True:
        response = requests.get(url=vm_id, headers=headers)
        response.raise_for_status()
        state=None; ip=None; state_found=False; ip_found=False;
        for line in response.text.splitlines():
            if "state" in line:
                state_found=True;
                state = line.split("'")[1]
            elif "net_interface.0.ip" in line:
                ip_found=True;
                ip = line.split("'")[1]
            if state_found and ip_found:
                break
        msg='{0} VM: {1}, State: {2}, IP: {3} '.format(get_log_indentation(), str(vm_id), str(state), str(ip))
        if state and state == 'configured' and ip:
            ip = create_child(dictionary=ctx.instance.runtime_properties, key='ip', value=ip)
            break
        elif not state or state == 'failed':
            raise NonRecoverableError('Deployment ERROR: '+msg)
        ctx.logger.debug(msg)
        time.sleep(timestep)
    decrease_log_indentation()

def start():
    reset_log_indentation()
    ctx.logger.debug('{0} Start operation: Begin'.format(get_log_indentation()))
    increase_log_indentation()
    infrastructure_id = get_child(dictionary=ctx.instance.runtime_properties, key='infrastructure_id', required=True)
    radl = get_child(dictionary=ctx.instance.runtime_properties, key='radl', required=True)
    headers = get_child(dictionary=ctx.instance.runtime_properties, key='headers', required=True)
    response = requests.post(url=infrastructure_id, data=radl, headers=headers)
    ctx.logger.debug('{0} Response code: {1}'.format(get_log_indentation(), str(response.status_code)))
    ctx.logger.info('{0} Virtual Machine ID: {1}'.format(get_log_indentation(), response.text))
    response.raise_for_status()
    vm_id = create_child(ctx.instance.runtime_properties, key='vm_id', value=response.text)
    ctx.logger.debug('{0} Waiting for the VM to be configured ...'.format(get_log_indentation()))
    wait_for_configuration(15)
    decrease_log_indentation()
    ctx.logger.debug('{0} Start operation: End'.format(get_log_indentation()))

if (not get_child(dictionary=inputs, key='simulate', required=False)):
    try:
        start()
    except Exception as ex:
        ctx.logger.error('ERROR: {0}'.format(str(ex)))

