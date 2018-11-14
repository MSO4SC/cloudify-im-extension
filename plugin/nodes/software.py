from cloudify import ctx
from cloudify.state import ctx_parameters as inputs
from cloudify.decorators import operation
from cloudify.exceptions import *
from plugin.nodes.utils import *

def build_radl_software(config):
    ctx.logger.debug('{0} Infrastructure Manager deployment info:'.format(get_log_indentation()))
    increase_log_indentation()

    print(str(inputs))
    name   = get_child(dictionary=inputs, key='name' ) or 'software'
    packages = get_child(dictionary=config, key='packages') or []
    deploy = get_child(dictionary=config, key='deploy', required=True)

    deploy_radl = "configure "+ str(name) + " (" + \
"""
@begin
- tasks:
  - name: """ + str(name) + " dependencies " + \
"""
    yum:
      name: "{{ packages }}"
    vars:
      packages:
"""
    for package in packages:
        deploy_radl += "        - " + str(package) + "\n"

    deploy_radl += "  - name: " + str(name) + \
"""
    args:
      chdir: /tmp
      executable: /bin/bash
    shell: |
"""
    for line in deploy.splitlines():
        deploy_radl += "        " + line  + "\n"

    deploy_radl += \
"""
@end
)
"""

    deploy_radl += \
"""
contextualize (
"""
    deploy_radl += "system node configure " + str(name) + " with Ansible \n" 
    deploy_radl += \
"""
)
"""

    decrease_log_indentation()
    return deploy_radl

@operation
def configure(config, simulate, **kwargs):
    if (not simulate):
        reset_log_indentation()
        ctx.logger.debug('{0} Configure operation: Begin'.format(get_log_indentation()))
        increase_log_indentation()
        radl = get_child(ctx.instance.runtime_properties, key='settings')
        if not radl:
            radl = create_child(ctx.instance.runtime_properties, key='settings', value={})
        radl_software = create_child(radl, key='software', value=build_radl_software(config))
        decrease_log_indentation()
        ctx.logger.debug('{0} Configure operation: End'.format(get_log_indentation()))

