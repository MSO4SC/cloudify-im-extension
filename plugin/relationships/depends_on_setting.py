from cloudify import ctx
from cloudify.state import ctx_parameters as inputs
from cloudify.decorators import operation
from cloudify.exceptions import *
from plugin.relationships.utils import *

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
    

