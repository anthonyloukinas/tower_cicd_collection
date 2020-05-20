# tower_cicd collection

Ansible Engine Modules to assist in exporting/importing content from Ansible Tower. You get the choice of exporting to flat file .yaml/.json definitions, which could be stored in Git, or NFS, or importing directly to a target Ansible Tower destination.

Features:

- Regex naming schema filter support (Ex: ORG_REGION_LANE_)
- Exporting assets to flat file (.json/.yaml)
- Exporting & Importing assets directly to a target Ansible Tower node

Assets supported:

- Projects
- Job_templates
- Workflow_job_templates
- Credentials (If database secret_key is provided)

## Usage

To be added.

## Authors

- Anthony Loukinas <<anthony.loukinas@redhat.com>>