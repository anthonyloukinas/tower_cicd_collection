#!/usr/bin/python

# Copyright: (c) 2020, Anthony Loukinas <anthony.loukinas@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# REMOVE THIS BEFORE PRODUCTION
# uri module - https://github.com/ansible/ansible/blob/stable-2.9/lib/ansible/modules/net_tools/basics/uri.py

ANSIBLE_METADATA = {
    'metadata_version': '2.9',
    'status': ['preview'],
    'supported_by': 'community'
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
    type:
        description:
            - Tower asset type
        type: str
        required: true
        choices:
            - project
            - job_template
            - workflow_job_template
    naming_filter:
        description:
            - Regex filter to enforce your assets naming standards properly
        type: str
        required: false
    src_tower:


author:
    - Anthony Loukinas (@anthonyloukinas)
'''

EXAMPLES = r'''
- name: Transport tower project to destination tower instance
  anthonyloukinas.tower_cicd.tower_export_asset:
    name: test
    type: project
    naming_filter: ''
    project:
      organization: 'prod_ops' # force target organization
    src_tower:
      host: 'http://localhost:8081'
      username: admin
      password: password
      verfiy_certs: False
      oath: 'not_supported_yet'
      secret_key: aabbcc
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
from ansible_collections.anthonyloukinas.tower_cicd.plugins.module_utils.tower import TowerRestClient, TowerConnectionError, TowerResourceNotFound, TowerAssetExists

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
            resolve_dependencies=dict(type="bool", required=False, defaults=False),
            update_asset=dict(type="bool", required=False, defaults=False),
            project=dict(
                type='dict',
                required=False,
                options=dict(
                    test=dict(type="str", required=False),
                    allow_override=dict(type="bool", required=False),
                    description=dict(),
                    name=dict(type="str", required=False),
                    scm_branch=dict(type="str", required=False),
                    scm_clean=dict(type="bool", required=False, choices=[True, False]),
                    scm_delete_on_update=dict(type="bool", required=False, choices=[True, False]),
                    scm_refspec=dict(type="str", required=False),
                    scm_type=dict(type="str", required=False, choices=["manual", "git", "hg", "svn"]),
                    scm_update_cache_timeout=dict(type="int", required=False),
                    scm_update_on_launch=dict(type="bool", required=False, choices=[True, False]),
                    scm_url=dict(type="str", required=False),
                    timeout=dict(type="int", required=False),
                )
            ),
            job_template=dict(
                type='dict',
                required=False,
                options=dict(
                    test=dict(type="str", required=False),
                )
            ),
            workflow_job_template=dict(
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
                    secret_key=dict(type="str", required=False),
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
        asset=None,
        status=None
    )

    # Storing local copies of module variables
    asset_name = module.params["name"]
    asset_type = module.params["type"]

    resolve_dependencies = module.params["resolve_dependencies"]
    update_asset = module.params["update_asset"]

    src_tower = module.params["src_tower"]
    dest_tower = module.params["dest_tower"]
    
    project = module.params["project"]
    job_template = module.params["job_template"]
    workflow_job_template = module.params["workflow_job_template"]

    # TODO support oath
    # TODO check for validate_certs?
    src_tower_client = TowerRestClient(
        address=src_tower["host"],
        username=src_tower["username"],
        password=src_tower["password"]
    )

    dest_tower_client = TowerRestClient(
        address=dest_tower["host"],
        username=dest_tower["username"],
        password=dest_tower["password"]
    )

    try:
        asset = src_tower_client.export_asset(asset_type, asset_name, resolve_dependencies)
        result["asset"] = asset

        # TODO we probably want to check the asset type first? So we dont overset values if the user is an idiot and
        #  sets these vars
        if project:
            for key in project:
                if project[key]:
                    asset[key] = project[key]

        if job_template:
            for key in job_template:
                if job_template[key]:
                    asset[key] = job_template[key]

        if workflow_job_template:
            for key in workflow_job_template:
                if workflow_job_template[key]:
                    asset[key] = job_template

        # DEBUG CODE FOR IMPORTING INTO NEXT TOWER INSTANCE
        status = dest_tower_client.import_asset(asset, update_asset)
        result["status"] = status

        module.exit_json(**result)

    except (TowerResourceNotFound, TowerConnectionError, TowerAssetExists) as e:
        module.fail_json(msg=e.message, **result)


if __name__ == '__main__':
    main()
