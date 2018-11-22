from cloudify import ctx
from cloudify.state import ctx_parameters as inputs
from cloudify.decorators import operation
from cloudify.exceptions import *
from plugin.nodes.utils import *

def build_radl_image(config):
    ctx.logger.debug('{0} Infrastructure Manager deployment info:'.format(get_log_indentation()))
    increase_log_indentation()

    id = get_child(dictionary=config, key='id', required=True)
    storage = get_child(dictionary=config, key='storage')
    username = get_child(dictionary=config, key='username') or 'user'
    password = get_child(dictionary=config, key='password')

    image_radl = ''
    image_radl += "    disk.0.image.url = '" + str(id) + "' and \n"
    image_radl += "    disk.0.os.credentials.username = '" + str(username) + "' and \n"
    if storage: image_radl += "    disk.0.image.size = '" + str(storage) + "' and \n" 
    if password: image_radl += "    disk.0.os.credentials.password = '" + str(password) + "' and \n"

    decrease_log_indentation()
    return image_radl

@operation
def configure(config, simulate, **kwargs):
    if (not simulate):
        reset_log_indentation()
        ctx.logger.debug('{0} Configure operation: Begin'.format(get_log_indentation()))
        increase_log_indentation()
        radl = get_child(ctx.instance.runtime_properties, key='settings')
        if not radl:
            radl = create_child(ctx.instance.runtime_properties, key='settings', value={})
        radl_image = create_child(radl, key='image', value=build_radl_image(config))
        decrease_log_indentation()
        ctx.logger.debug('{0} Configure operation: End'.format(get_log_indentation()))

    

