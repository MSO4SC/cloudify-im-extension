import requests
from cloudify import ctx
from cloudify.exceptions import *
from cloudify.state import ctx_parameters as inputs


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


def create():
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

#    ctx.logger.info('Create server')
#    ctx.logger.info('Just logging the node instance: {0}'
#                    .format(str(ctx.instance)))
#    ctx.logger.info('Just logging the runtime properties: {0}'
#                    .format(str(ctx.instance.runtime_properties)))
#    ctx.logger.info('The config operation input is : {0}'
#                    .format(str(inputs)))

    
if (not get_child(dictionary=inputs, key='simulate', required=False)):
    create()



