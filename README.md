# cloudify-im-extension
Cloudify extension to work with Infrastructure Manager (Skeleton)

## Hello world

* Copy the repository contents into _[BLUEPRINT_ROOT]/cloudify-im-extension/_
* Create a new file _[BLUEPRINT_ROOT]/blueprint.yaml_ with the following content:

````yaml
imports:
  - http://www.getcloudify.org/spec/cloudify/4.3/types.yaml
  - cloudify-im-extension/im.yaml


node_templates:
  example_vm:
    type: im.nodes.Server
    properties:
        config:
            user: user
            pass: pass
            image: ubuntu
            flavor: tiny
        resource_id: vm_test

  example_network:
    type: im.nodes.Network
    properties:
        use_external_resource: true
        resource_id: default_network
    relationships:
        - type: setting_contained_in
          target: example_vm
````
