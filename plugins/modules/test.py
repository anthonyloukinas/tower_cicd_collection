ANSIBLE_METADATA = {
    'metadata_version': '2.9',
    'status': ['preview'],
    'supported_by': 'Anthony Loukinas <anthony.loukinas@redhat.com>'
}


EXAMPLES = '''
# TBA

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
'''

# Imports
import pdb


# Ansible Dependencies
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.aloukinas_modules.pipeline.plugins.module_utils.tower import TowerRestClient

# The AnsibleModule object
module = None

def main():

    global module

    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type="str", required=True),
            type=dict(type="str", required=True),
            project=dict(
                test=dict(type="str", required=False)
            ),
            target_tower=dict(
                host=dict(type="str", required=False),
                username=dict(type="str", required=False),
                password=dict(type="str", required=False),
                verify_certs=dict(type="bool", required=False),
                oauth=dict(type="str", required=False),
            )
        ),
        supports_check_mode=False,
    )

    result = dict(
        changed=False,
        response=True,
        asset=None
    )

    name = module.params["name"]
    asset_type = module.params["type"]
    target_tower = module.params["target_tower"]
    project = module.params["project"]

    if asset_type == "project":
        result["asset"] = "project"

    if asset_type == "job_template":
        result["asset"] = "job_template"
    
    if asset_type == "workflow_job_template":
        result["asset"] = "workflow_job_template"

    module.exit_json(**result)
    


    # tower_client = TowerRestClient(
    #     address=
    # )


    


if __name__ == '__main__':
    main()
