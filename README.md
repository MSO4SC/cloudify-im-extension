# cloudify-im-extension
Cloudify extension to work with Infrastructure Manager (Skeleton)

Note: This plugin has been tested against OCCI endpoints only. Minor modifications are required to support other cloud providers.

## Hello world

* Copy the repository contents into _[BLUEPRINT_ROOT]/cloudify-im-extension/_
* Create a new file _[BLUEPRINT_ROOT]/blueprint.yaml_ with the following content:

````yaml
tosca_definitions_version: cloudify_dsl_1_3

imports:
  - http://raw.githubusercontent.com/mso4sc/cloudify-hpc-plugin/master/resources/types/cfy_types.yaml
  - http://raw.githubusercontent.com/MSO4SC/cloudify-im-extension/master/im.yaml


node_templates:
    vitual_machine:
        type: im.nodes.Server
        properties:
            config:
                id: im
                host: 'http://im.srv.cesga.es:8800'
                type: InfrastructureManager
                user: ... # IM user
                pass: ... # IM password
                endpoint:
                    id: occi
                    type: OCCI
                    host: 'https://fedcloud-services.egi.cesga.es:11443'
                    proxy: '...'
            resource_id: vm_test
            simulate: False
        relationships:
            - type: depends_on_setting
              target: network
            - type: depends_on_setting
              target: image
            - type: depends_on_setting
              target: keypair
            - type: depends_on_setting
              target: flavour


    network:
        type: im.nodes.Network
        properties:
            name: net
            config: 
                outbound: True
            use_external_resource: true
            resource_id: default_network
            simulate: False

    image:
        type: im.nodes.Image
        properties:
            name: Centos-7
            config: 
                id: 'https://fedcloud-services.egi.cesga.es:11443/51'
                storage: 1024M
                username: ... # Optional
                password: ... # Optional
            use_external_resource: true
            resource_id: default_image
            simulate: False

    keypair:
        type: im.nodes.Keypair
        properties:
            name: Credentials
            config: 
                id: 'user@laptop'
                public_key: 'ssh-rsa ...' # Optional
                private_key: | # Optional
                    -----BEGIN RSA PRIVATE KEY-----
                    ...
                    -----END RSA PRIVATE KEY-----
            use_external_resource: true
            resource_id: default_image
            simulate: False

    flavour:
        type: im.nodes.Flavour
        properties:
            name: small
            config: 
                type: small
                cores: 1
                memory: 1024M
            use_external_resource: true
            resource_id: default_flavour
            simulate: False

    software:
        type: im.nodes.Software
        properties:
            name: singularity-openmpi
            config: 
                packages: ["openmpi", "singularity"]
                deploy: |
                    ln -s /usr/lib64/openmpi/bin/mpirun /usr/bin/mpirun
            use_external_resource: true
            resource_id: default_software
            simulate: False

````

## Infrastructure Manager

This plugin connects to an [Infrastructure Manager](http://www.grycap.upv.es/im/index.php) instance to manage the deployment of virtual machines.

# Template

Previous template maps the *Resource and Application Description Language* (RADL) specification to cloudify node types. Basic RADL structure can be found in the official [RADL docs](https://imdocs.readthedocs.io/en/latest/radl.html#basic-structure). In this docs you can see how to reference OCCI endpoints and images.
