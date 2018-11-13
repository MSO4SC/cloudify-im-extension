########
# Copyright (c) 2014 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.

""" Setuptools module file """
from setuptools import setup

# Replace the place holders with values for your project

setup(

    # Do not use underscores in the plugin name.
    name='im',

    version='0.0.1',
    author='Victor Sande',
    author_email='vsande@cesga.es',
    description='Plugin to use IM from Cloudify',

    # This must correspond to the actual packages in the plugin.
    packages=['plugin',
              'plugin.nodes',
              'plugin.nodes.flavour',
              'plugin.nodes.image',
              'plugin.nodes.network',
              'plugin.nodes.server',
              'plugin.nodes.software',
              'plugin.relationships',
              'plugin.relationships.depends_on_setting'],

    zip_safe=False,
    install_requires=[
        # Necessary dependency for developing plugins, do not remove!
        "cloudify-plugins-common",
        "requests"
    ],
    license='LICENSE'
)
