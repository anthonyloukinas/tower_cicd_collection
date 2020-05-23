# This code is part of Ansible, but is an independent component.
# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
# to the complete work.
#
# Copyright (c), Anthony Loukinas <anthony.loukinas@redhat.com>, 2020
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE
#


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json

from ansible.module_utils.urls import Request, ConnectionError
from ansible.module_utils.six.moves.urllib.error import HTTPError, URLError

PROJECT_FIELDS_TO_REMOVE = [
    'id',
    'url',
    'related',
    'summary_fields',
    'created',
    'modified',
    'local_path',
    'credential', # needs replacing
    'scm_revision',
    'last_job_run',
    'last_job_failed',
    'next_job_run',
    'status',
    'organization', # needs replacing
    'custom_virtualenv',
    'last_update_failed',
    'last_updated'
]


class Error(Exception):
    pass


class TowerResourceNotFound(Error):
    def __init__(self, message, response=None):
        self.message = message
        self.response = response


class TowerConnectionError(Error):
    def __init__(self, message, response=None):
        self.message = message
        self.response = response

class TowerAssetExists(Error):
    def __init__(self, message, response=None):
        self.message = message
        self.response = response

class TowerRestClient:

    def __init__(self, address, username, password, validate_certs=False, force_basic_auth=True):
        self._address = address
        self._username = username
        self._password = password
        self._validate_certs = validate_certs
        self._force_basic_auth = force_basic_auth
        self._headers = {}
        self._client = Request()

    def _request(self, method, path, payload=None):
        headers = self._headers.copy()
        data = None
        if payload:
            data = json.dumps(payload)
            headers["Content-Type"] = "application/json"

        url = self._address + path
        try:
            r = self._client.open(method, url, data=data, headers=headers, validate_certs=self._validate_certs, url_username=self._username, url_password=self._password, force_basic_auth=self._force_basic_auth)
            r_status = r.getcode()
            r_headers = dict(r.headers)
            data = r.read().decode("utf-8")
            r_data = json.loads(data) if data else {}
        except HTTPError as e:
            r_status = e.code
            r_headers = {}
            r_data = dict(msg=str(e.reason))
        except (ConnectionError, URLError) as e:
            raise AnsibleConnectionFailure(
                "Could not connect to {0}: {1}".format(url, e.reason)
            )
        return r_status, r_headers, r_data

    def get(self, path):
        return self._request("GET", path)

    def post(self, path, payload=None):
        return self._request("POST", path, payload)

    def patch(self, path, payload=None):
        return self._request("PATCH", path, payload)

    def delete(self, path):
        return self._request("DELETE", path)

    def asset_exists(self, asset_name, asset_type):
        _status, _headers, _data = self.get('/api/v2/{}/?name={}'.format(asset_type, asset_name))

        if _data.get('count') != 0:
            return _data
        else:
            return None

    # EXPORTS
    def _export_project(self, name, resolve_dependencies):
        _status, _headers, _data = self.get('/api/v2/projects/?name={}'.format(name))

        # Check HTTP status code for request
        if _status != 200:
            raise TowerConnectionError("Ansible expected an HTTP response code of {} but got {}".format(200, _status))
        else:
            # Check if we found an asset matching provided name
            if _data["count"] == 0:
                raise TowerResourceNotFound("Project named {} was not found".format(name))
            else:
                # Store local copy of project json
                project = _data["results"][0]
                
                # Remove fields that cannot be imported
                for field in PROJECT_FIELDS_TO_REMOVE:
                    del(project[field])

                return project

    def _export_job_template(self, name, resolve_dependencies):
        pass

    def _export_workflow_job_template(self, name, resolve_dependencies):
        pass

    def export_asset(self, asset_type, asset_name, resolve_dependencies):

        if asset_type == "project":
            return self._export_project(asset_name, resolve_dependencies)

        elif asset_type == "job_template":
            return self._export_job_template(asset_name, resolve_dependencies)

        elif asset_type == "workflow_job_template":
            return self._export_workflow_job_template(asset_name, resolve_dependencies)

    # IMPORTS
    def _import_project(self, project, update_asset):

        result = dict(
            imported=False,
            request=None
        )

        success_codes = [200, 201, 202, 203]

        asset_exists = self.asset_exists(project["name"], 'projects')

        if asset_exists:
            asset_id = asset_exists["results"][0]["id"]
            if update_asset:
                _status, _headers, _data = self.patch('/api/v2/projects/{}/'.format(asset_id), project)
            else:
                # raise error that asset already exists, try using update_asset if you want to override it
                raise TowerAssetExists(
                    message="An asset named '{}' already exists. If you'd like to overwrite this assets variables, set 'update_asset: true' in your playbook".format(project["name"])
                )
        else:
            _status, _headers, _data = self.post('/api/v2/projects/', project)

        result["request"] = _status, _headers, _data

        if _status in success_codes:  # Successful import
            result["imported"] = True
            return result
        else:
            return result  # return error here

    def import_asset(self, asset, update_asset):

        if asset["type"] == "project":
            return self._import_project(asset, update_asset)