from cloudify import ctx
from cloudify.state import ctx_parameters as inputs
from cloudify.decorators import operation
from cloudify.exceptions import *
from plugin.nodes.utils import *
import paramiko
import StringIO

def build_radl_keypair(config):
    ctx.logger.debug('{0} Infrastructure Manager deployment info:'.format(get_log_indentation()))
    increase_log_indentation()

    public_key = get_child(dictionary=config, key='public_key') or None
    private_key = get_child(dictionary=config, key='private_key') or None

    if not (public_key and private_key):
        increase_log_indentation()
        ctx.logger.debug('{0} Creating RSA keypair ...'.format(get_log_indentation()))
        private_key_stream = StringIO.StringIO()
        key = paramiko.RSAKey.generate(2048)
        public_key = '{0} {1}'.format(key.get_name().strip(), key.get_base64().strip())
        key.write_private_key(private_key_stream)
        private_key = private_key_stream.getvalue().strip()
        decrease_log_indentation()

    keypair_radl = ''
    keypair_radl += "    disk.0.os.credentials.public_key = '" + str(public_key.strip()) + "' and \n"
    keypair_radl += "    disk.0.os.credentials.private_key = '" + str(private_key.strip()) + "' "

    decrease_log_indentation()
    return keypair_radl

@operation
def configure(config, simulate, **kwargs):
    if (not simulate):
        reset_log_indentation()
        ctx.logger.debug('{0} Configure operation: Begin'.format(get_log_indentation()))
        increase_log_indentation()
        radl = get_child(ctx.instance.runtime_properties, key='settings')
        if not radl:
            radl = create_child(ctx.instance.runtime_properties, key='settings', value={})
        radl_image = create_child(radl, key='keypair', value=build_radl_keypair(config))
        decrease_log_indentation()
        ctx.logger.debug('{0} Configure operation: End'.format(get_log_indentation()))

    

