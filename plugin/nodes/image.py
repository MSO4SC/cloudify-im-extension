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


def build_radl_image():
    ctx.logger.debug('{0} Infrastructure Manager deployment info:'.format(get_log_indentation()))
    increase_log_indentation()

    config   = get_child(dictionary=inputs, key='config', required=True)
    id = get_child(dictionary=config, key='id', required=True)
    storage = get_child(dictionary=config, key='storage')
    username = get_child(dictionary=config, key='username', required=True)
    password = get_child(dictionary=config, key='password', required=True)
    public_key = get_child(dictionary=config, key='public_key', required=True)
    private_key = get_child(dictionary=config, key='private_key', required=True)

    image_radl = ''
    image_radl += "    disk.0.image.url = '" + str(id) + "' and \n"
    if storage: image_radl += "    disk.0.image.size = '" + str(storage) + "' and \n" 
    image_radl += "    disk.0.os.credentials.username = '" + str(username) + "' and \n"
    image_radl += "    disk.0.os.credentials.password = '" + str(password) + "' and \n"
    image_radl += "    disk.0.os.credentials.public_key = '" + str(public_key.strip()) + "' and \n"
    image_radl += "    disk.0.os.credentials.private_key = '" + str(private_key.strip()) + "' "

    decrease_log_indentation()
    return image_radl

@operation
def configure():
    if (not get_child(dictionary=inputs, key='simulate', required=False)):
        reset_log_indentation()
        ctx.logger.debug('{0} Configure operation: Begin'.format(get_log_indentation()))
        increase_log_indentation()
        radl = get_child(ctx.instance.runtime_properties, key='settings')
        if not radl:
            radl = create_child(ctx.instance.runtime_properties, key='settings', value={})
        radl_image = create_child(radl, key='image', value=build_radl_image())
        decrease_log_indentation()
        ctx.logger.debug('{0} Configure operation: End'.format(get_log_indentation()))

    

