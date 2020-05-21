# REMOVE THIS BEFORE PRODUCTION
# uri module - https://github.com/ansible/ansible/blob/stable-2.9/lib/ansible/modules/net_tools/basics/uri.py
#

ANSIBLE_METADATA = {
    'metadata_version': '2.9',
    'status': ['preview'],
    'supported_by': 'Anthony Loukinas <anthony.loukinas@redhat.com>'
}

DOCUMENTATION = r'''
---
module: tower_export_asset
short_description: Aids in exporting and importing tower assets
description:
    - Aids in exporting and importing tower assets
version_added: "2.9"
options:
  name:
    description:
        - Name of asset to export
    type: str
    required: true
'''

EXAMPLES = r'''
- name: Export tower project directly to another Tower node
  tower_export_content:
    name: '*' # str or *
    type: project # project, job_template, workflow
    naming_filter: '' # regex string
    project: 
      organization: 'prod_ops' # force target organization
    target_tower:
      host: 'http://production.tower.company.com' #required
      username: 'admin' #required
      password: 'password' #required
      verify_certs: False #optional
      oauth: 'not_supported_yet' #optional


- name: Transport tower project to destination tower instance
  anthonyloukinas.tower_cicd.tower_export_asset:
    name: test
    type: project
    src_tower:
      host: 'http://localhost:8081'
      username: admin
      password: password
    dest_tower:
      host: 'http://localhost:8082'
      username: admin
      password: password
'''

RETURN = r'''
response:
    description: Fill this out Anthony
    returned: always
    type: str
    sample: test
'''

# Imports
import pdb
import json

# Ansible Dependencies
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.anthonyloukinas.tower_cicd.plugins.module_utils.tower import TowerRestClient

# The AnsibleModule object
module = None


def main():

    # Pulling in globally defined module
    global module

    # Building Ansible Module definition
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type="str", required=True),
            type=dict(type="str", required=True, choices=[
                'project',
                'job_template',
                'workflow_job_template',
                'unified_job_template'
            ]),
            project=dict(
                type='dict',
                required=False,
                options=dict(
                    test=dict(type="str", required=False),
                )
            ),
            src_tower=dict(
                type='dict',
                required=True,
                options=dict(
                    host=dict(type="str", required=False),
                    username=dict(type="str", required=False),
                    password=dict(type="str", required=False, no_log=True),
                    verify_certs=dict(type="bool", required=False),
                    oauth=dict(type="str", required=False),
                )
            ),
            dest_tower=dict(
                type='dict',
                required=False,
                options=dict(
                    host=dict(type="str", required=False),
                    username=dict(type="str", required=False),
                    password=dict(type="str", required=False, no_log=True),
                    verify_certs=dict(type="bool", required=False),
                    oauth=dict(type="str", required=False),
                )
            )
        ),
        supports_check_mode=False,
    )


    # Preparing result dictionary object
    result = dict(
        changed=False,
        response=True,
        asset=None
    )


    # Storing local copies of module variables
    asset_name = module.params["name"]
    asset_type = module.params["type"]

    src_tower = module.params["src_tower"]
    dest_tower = module.params["dest_tower"]
    
    project = module.params["project"]


    # TODO support oath
    # TODO check for validate_certs?
    src_tower_client = TowerRestClient(
        address=src_tower["host"],
        username=src_tower["username"],
        password=src_tower["password"]
    )

    res = src_tower_client.export_asset(asset_type, asset_name)

    result["res"] = res
    
    module.exit_json(**result)




if __name__ == '__main__':
    main()
