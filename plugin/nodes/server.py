import time
import requests
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

def build_request_headers():
    ctx.logger.debug('{0} Infrastructure Manager configuration info:'.format(get_log_indentation()))
    increase_log_indentation()
    config = get_child(dictionary=inputs, key='config', required=True)
    im_id = get_child(dictionary=config, key='id', required=True)
    im_type = get_child(dictionary=config, key='type', required=True)
    im_user = get_child(dictionary=config, key='user', required=True)
    im_pass = get_child(dictionary=config, key='pass', required=True)
    im_auth = "id = "+im_id+"; type = "+im_type+"; username = "+im_user+"; password = "+im_pass+";"
    decrease_log_indentation()

    ctx.logger.debug('{0} OCCI configuration info'.format(get_log_indentation()))
    increase_log_indentation()
    occi = get_child(dictionary=config, key='endpoint', required=True)
    occi_id = get_child(dictionary=occi, key='id', required=True)
    occi_type = get_child(dictionary=occi, key='type', required=True)
    occi_host = get_child(dictionary=occi, key='host', required=True)
    occi_proxy = get_child(dictionary=occi, key='proxy', required=True)
    decrease_log_indentation()
    occi_auth = "id = "+occi_id+"; type = "+occi_type+"; host = "+occi_host+"; proxy = "+occi_proxy+";"

    auth = im_auth+" \\n"+occi_auth
    headers = {
	    "Authorization" : auth,
	    "Content-type" : "text/plain"
    }

    return headers

def build_radl():
    ctx.logger.debug('{0} Infrastructure Manager deployment info:'.format(get_log_indentation()))
    increase_log_indentation()


    settings = get_child(ctx.instance.runtime_properties, key='settings', required=True)    
    network = get_child(settings, key='network') or ''
    image = get_child(settings, key='image', required=True)
    flavour = get_child(settings, key='flavour') or ''
    software = get_child(settings, key='software') or ''

    radl = \
network + \
"system node (\n" + \
"    instance_name = 'mso4sc' and \n" + \
"    net_interface.0.connection = 'net' and \n" + \
flavour + \
image + \
"""
)

deploy node 1
""" + \
software 

    decrease_log_indentation()
    return radl

def wait_for_configuration(timestep):
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

@operation
def configure():
    if (not get_child(dictionary=inputs, key='simulate', required=False)):
        reset_log_indentation()
        ctx.logger.debug('{0} Configure operation: Begin'.format(get_log_indentation()))
        increase_log_indentation()
        radl = create_child(ctx.instance.runtime_properties, key='radl', value=build_radl())
        decrease_log_indentation()
        ctx.logger.debug('{0} Configure operation: End'.format(get_log_indentation()))

@operation
def create():
    if (not get_child(dictionary=inputs, key='simulate', required=False)):
        reset_log_indentation()
        ctx.logger.debug('{0} Create operation: Begin'.format(get_log_indentation()))
        increase_log_indentation()
        config = get_child(dictionary=inputs, key='config', required=True)
        host = get_child(dictionary=config, key='host', required=True)
        headers = create_child(ctx.instance.runtime_properties, key='headers', value=build_request_headers())
        response = requests.post(url=host+'/infrastructures', data="", headers=headers)
        ctx.logger.debug('{0} Response code: {1}'.format(get_log_indentation(), str(response.status_code)))
        ctx.logger.info('{0} Infrastructure ID: {1}'.format(get_log_indentation(), response.text))
        response.raise_for_status()
        infrastructure_id = create_child(ctx.instance.runtime_properties, key='infrastructure_id', value=response.text)
        decrease_log_indentation()
        ctx.logger.debug('{0} Create operation: End'.format(get_log_indentation()))

@operation
def delete():
    if (not get_child(dictionary=inputs, key='simulate', required=False)):
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

@operation
def start():
    if (not get_child(dictionary=inputs, key='simulate', required=False)):
        try:
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
        except Exception as ex:
            ctx.logger.error('ERROR: {0}'.format(str(ex)))

@operation
def stop():
    if (not get_child(dictionary=inputs, key='simulate', required=False)):
        reset_log_indentation()
        ctx.logger.debug('{0} Stop operation: Begin'.format(get_log_indentation()))
        increase_log_indentation()
        headers = get_child(dictionary=ctx.instance.runtime_properties, key='headers', required=True)
        vm_id = get_child(dictionary=ctx.instance.runtime_properties, key='vm_id', required=True)
        if vm_id:
            response = requests.delete(url=vm_id, headers=headers)
            ctx.logger.debug('{0} Response code: {1}'.format(get_log_indentation(), str(response.status_code)))
            ctx.logger.info('{0} Virtual Machine ID: {1} deleted!'.format(get_log_indentation(), vm_id))
            response.raise_for_status()
        decrease_log_indentation()
        ctx.logger.debug('{0} Stop operation: End'.format(get_log_indentation()))




