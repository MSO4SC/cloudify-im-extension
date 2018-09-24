from cloudify import ctx
from cloudify.state import ctx_parameters as inputs

ctx.logger.info('Just logging the node instance id: {0}'
                .format(ctx.instance.properties['id']))
ctx.logger.info('The config operation input is : {0}'
                .format(inputs['config']))
