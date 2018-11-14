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

    

