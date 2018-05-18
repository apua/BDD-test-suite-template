import requests
from requests_toolbelt import MultipartEncoder
import json
import time
import os
import re
import zipfile
import StringIO
from robot.libraries.BuiltIn import BuiltIn
from ftplib import FTP
import cirrus_rest

requests.packages.urllib3.disable_warnings()

class CirrusRESTLib(object):
    def __init__(self, ip):
        self.base_url = 'https://' + ip
        self.apiVersion = 100
        self.headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        self.username = 'Administrator'
        self.password = 'Compaq123'
        self.builtin = BuiltIn()

    def login_cirrus(self, username, password, domain='LOCAL'):
        """Login Cirrus.
        Args:
            username: login user name.
            password: login user password.

        Returns:
            Return 200 if operation is successfully. Otherwise the operation
            fails.
        """
        self.username = username
        self.password = password
        self.domain = domain
        url = self.base_url + cirrus_rest.uri.get('login_sessions')
        payload = {'userName': self.username, 'password': self.password, 'authLoginDomain': self.domain}
        data = json.dumps(payload).encode('utf-8')
        headers = self.headers
        r = requests.post(url=url, data=data, headers=headers, verify=False)
        if r.status_code == 200:
            self.sessionID = r.json()['sessionID']
            headers['auth'] = self.sessionID
        self.builtin.log_to_console(r.json())
        return r.status_code

    def get_session_id(self):
        """Get login session id.
        
        Returns:
            Return a sessionID.
        """
        if not hasattr(self, 'sessionID') or self.sessionID is None:
            self.login_cirrus(self.username, self.password)
        self.builtin.log_to_console("Get sessionID %s" % self.sessionID)
        return self.sessionID

    def wait_for_cirrus_to_start(self, username, password):
        time_count = 0
        while True:
            try:
                r = self.login_cirrus(username, password)
            except requests.exceptions.RequestException:
                continue
            if r == 503:
                self.builtin.log_to_console("Wait for Cirrus to start...")
                time.sleep(30)
                time_count = time_count + 1
                # over 20 min, error out
                if time_count > 40:
                    raise AssertionError("Cirrus unable to bootup for over 20 min")
                continue
            else:
                break
        

    def save_eula(self):
        """REST API to save EULA.

        Returns:
            Return 200 if operation is successfully. Otherwise the operation
            fails.
        """
        url = self.base_url + cirrus_rest.uri.get('eula_save')
        payload = {'supportAccess': 'yes'}
        data = json.dumps(payload).encode('utf-8')
        headers = self.headers
        r = requests.post(url=url, data=data, headers=headers, verify=False)
        self.builtin.log_to_console(r.json())
        return r.status_code

    def change_initial_password(self, old_password, new_password):
        """REST API to change default password.

        Args:
            old_password: default Cirrus password.
            new_password: new password.

        Returns:
            Return 200 if operation is successfully. Otherwise the operation
            fails.
        """
        url = self.base_url + cirrus_rest.uri.get('change_password')
        payload = {'userName': 'Administrator', 'oldPassword': old_password, 'newPassword': new_password}
        data = json.dumps(payload).encode('utf-8')
        headers = self.headers
        r = requests.post(url=url, data=data, headers=headers, verify=False)
        self.builtin.log_to_console(r.json())
        return r.status_code

    def get_network_configuration(self):
        """Get network config.

        Returns:
            Return 200 if operation is successfully. Otherwise the operation
            fails.
        """
        url = self.base_url + cirrus_rest.uri.get('network_interfaces')
        headers = self.headers
        headers['X-Api-Version'] = 300
        if 'auth' not in self.headers:
            headers['auth'] = self.get_session_id()
        r = requests.get(url=url, headers=headers, verify=False)
        self.network_info = r.json()
        return r.status_code

    def set_init_network(self):
        """Set network hostname and DHCP.

        Returns:
            Return 200 if operation is successfully. Otherwise the operation
            fails.
        """
        status = self.get_network_configuration()
        if status != 200:
            self.builtin.log_to_console("Get network config failed. status code:%s" % status)
            return status
        payload = self.network_info
        url = self.base_url + cirrus_rest.uri.get('network_interfaces')
        payload['applianceNetworks'][0]['app1Ipv4Addr'] = ''
        payload['applianceNetworks'][0]['overrideIpv4DhcpDnsServers'] = False
        payload['applianceNetworks'][0]['ipv4Type'] = 'DHCP'
        payload['applianceNetworks'][0]['hostname'] = 'cirrus.net'
        data = json.dumps(payload).encode('utf-8')
        headers = self.headers
        headers['X-Api-Version'] = 300
        if 'auth' not in self.headers:
            headers['auth'] = self.get_session_id()
        r = requests.post(url=url, data=data, headers=headers, verify=False)
        return r.status_code

    def wait_until_network_config_done(self):
        """Wait until the network config takes effect.

        Returns:
            Return 0 if operation is successfully. Otherwise the operation
            fails.
        """
        url = self.base_url + cirrus_rest.uri.get('task')
        headers = self.headers
        if 'auth' not in self.headers:
            headers['auth'] = self.get_session_id()
        for i in range(0,6):
            r = requests.get(url=url, headers=headers, verify=False)
            percent = r.json()['members'][-1]['percentComplete']
            self.builtin.log_to_console("Complete %s/100 network config" % percent)
            time.sleep(30)
        r = requests.get(url=url, headers=headers, verify=False)
        task = r.json()['members'][-1]
        if r.status_code == 200 and task['percentComplete'] == 100:
            return 0
        else:
            self.builtin.log_to_console("Status code: %s, percentComplete: %s, taskState: %s" % (r.status_code, task['percentComplete'], task['taskState']))
            return r.status_code

    def upload_fw_image(self):
        """Upload upgrade file image.

        Returns:
            Return 200 if operation is successfully. Otherwise the operation
            fails.
        """
        ftp = FTP(cirrus_rest.DEV_NFS)
        ftp.login(cirrus_rest.nfs_user, cirrus_rest.nfs_pw)
        ftp.retrbinary("RETR /Public/Cirrus_OVF_mat/"+self.to_version+"/"+self.upgrade_file, open(self.upgrade_file,'wb').write)
        ftp.close()
        url = self.base_url + cirrus_rest.uri.get('upload_image')
        m = MultipartEncoder(
            fields={'file': (self.upgrade_file, open(self.upgrade_file, 'rb'), 'application/octet-stream')}
            )
        headers = self.headers
        if 'auth' not in self.headers:
            headers['auth'] = self.get_session_id()
        headers['X-Api-Version'] = 300
        headers['Content-Type'] = m.content_type
        r = requests.post(url=url, data=m, headers=headers, verify=False)
        self.builtin.log_to_console(r.json())
        return r.status_code

    def install_image(self):
        """Install the upgrade file.

        Returns:
            Return 200 if operation is successfully. Otherwise the operation
            fails.
        """
        url = self.base_url + cirrus_rest.uri.get('install_image') + self.upgrade_file
        headers = self.headers
        if 'auth' not in self.headers:
            headers['auth'] = self.get_session_id()
        r = requests.put(url=url, headers=headers, verify=False)
        return r.status_code

    def get_upgrade_status(self):
        """ Get upgrade progress status.

        Returns:
            Return upgrade status object.
        """
        url = self.base_url + cirrus_rest.uri.get('upgrade_status')
        headers = self.headers
        if 'auth' not in self.headers:
            headers['auth'] = self.get_session_id()
        r = requests.get(url=url, headers=headers, verify=False)
        self.builtin.log_to_console(r.json())
        return r.status_code

    def upgrade_appliance(self, to_version, upgrade_file):
        """Upgrade appliance.

        Args:
            to_version: the version that the appliance should update to.
            upgrade_file: filename of the upgrade file.

        Returns:
            Return 0 if operation is successfully. Otherwise the operation
            fails.
        """
        self.builtin.log_to_console("Uploading image...")
        self.to_version = to_version
        self.upgrade_file = upgrade_file
        status = self.upload_fw_image()
        if status != 200:
            self.builtin.log_to_console("Uploading image failed. status code:%s" % status)
            return status
        self.builtin.log_to_console("Installing image...")
        status = self.install_image()
        if status != 202:
            self.builtin.log_to_console("Installing image failed. status code:%s" % status)
            return status
        # count for upgrade time
        time_count = 0
        # delay for 20s
        time.sleep(20)
        while True:
            r = self.get_upgrade_status()
            # exit loop and mark test pass if completing upgrade or waiting over 40 min
            if r == 200:
                return 0
            # exit loop and mark test fail if waiting over 40 min
            elif time_count >= 4:
                return -1
            # wait for 10 min
            else:
                time.sleep(600)
                time_count = time_count + 1

    def add_hardware(self, sut_list_file):
        """Use REST API to add a list of HWs.

        Args:
            sut_list_file: file that contains list of HW data.
            example:

            for general HW:

            [{"name": "test1", "type": "ilo"}]
            
            for HW group:

            {"name": "test1", "type": "group", "hw_group": "true", "group_member":[1,2,3]}

        Returns:
            Return 200 if add action is successful. Otherwise the operation
            fails.
        """
        with open(sut_list_file, 'r') as f:
            self.suts = json.load(f)
        headers = self.headers
        if 'auth' not in self.headers:
            headers['auth'] = self.get_session_id()
        for sut in self.suts:
            self.builtin.log_to_console(sut)
            if 'hw_group' in sut and sut['hw_group'] == 'true':
                url = self.base_url + cirrus_rest.uri.get('hardware_group')
                payload = sut
            else:
                url = self.base_url + cirrus_rest.uri.get('hardware')
                payload = [sut]
            data = json.dumps(payload).encode('utf-8')
            r = requests.post(url=url, data=data, headers=headers, verify=False)
            if r.status_code != 200:
                self.builtin.log_to_console("Adding HW failed. status code:%s, sut:%s" % (r.status_code, sut))
                return r.status_code
            if 'hw_group' not in sut:
                self.builtin.log_to_console(r.json())
        return r.status_code

    def edit_hardware(self, sut_id, attr, attr_value):
        """Edit HW scenario. Use GET/POST REST API to edit a HW and check if
        the modification takes effect.

        Args:
            sut_id: Cirrus HW id.
            attr: Cirrus HW attribute.
            attr_value: Cirrus HW attribute value.
            
        Returns:
            Return 200 if the actions are successful. Otherwise the operation
            fails.
        """
        url = self.base_url + cirrus_rest.uri.get('hardware') + '/' + str(sut_id)
        headers = self.headers
        r = requests.get(url=url, headers=headers, verify=False)
        if r.status_code != 200:
            self.builtin.log_to_console("Fetching HW failed. status code:%s, sut_id:%s" % (r.status_code, sut_id))
            return r.status_code
        payload = r.json()
        # remove hw_wwid because the format of this value cannot be used in PUT method later
        payload.pop('hw_wwid', None)
        if attr == 'group_member':
            attr_value = attr_value.split(',')
            for i in range(len(attr_value)):
                attr_value[i] = int(attr_value[i])
        payload[attr] = attr_value
        data = json.dumps(payload).encode('utf-8')
        if 'auth' not in self.headers:
            headers['auth'] = self.get_session_id()
        r = requests.put(url=url, data=data, headers=headers, verify=False)
        self.builtin.log_to_console(r.json())
        r = requests.get(url=url, headers=headers, verify=False)
        if attr == 'group_member':
            # ignore checking PUT response for group_member attribute since no group_member value will be returned
            check_value = attr_value
            # check hw group children and get status
            hwg = self.check_hw_group_relations(sut_id, attr_value)
        else:
            check_value = r.json()[attr]
            hwg = True
        if r.status_code != 200:
            self.builtin.log_to_console("Updating HW failed. status code:%s, sut_id:%s" % (r.status_code, sut_id))
            return r.status_code
        if check_value != attr_value or hwg == False:
            self.builtin.log_to_console("Updating HW failed. Compare error. %s sut_id:%s" % (check_value, sut_id))
            return -1
        return r.status_code

    def check_hw_group_relations(self, sut_id, expect_children):
        """Compare HW group children.

        Args:
            sut_id: Cirrus HW id.
            expect_children: expect children list.
            
        Returns:
            Return True if the expect_children list is the same as HW chilren list from HWDB. Otherwise return False.
        """
        url = self.base_url + cirrus_rest.uri.get('hardware_group') + '/' + str(sut_id)
        headers = self.headers
        if 'auth' not in self.headers:
            headers['auth'] = self.get_session_id()
        r = requests.get(url=url, headers=headers, verify=False)
        if r.status_code != 200:
            self.builtin.log_to_console("Get HW failed. status code:%s, sut:%s" % (r.status_code, sut_id))
            return False
        get_ch_list = r.json()['children']
        ch_hwdb = []
        for child in get_ch_list:
            ch_hwdb.append(child['id'])
        if ch_hwdb == sorted(expect_children):
            return True
        else:
            return False

    def delete_hardware(self, sut_id):
        """Use REST API to delete a HW and GET the HW to check if it still
        exists.

        Args:
            sut_id: Cirrus HW id.
            
        Returns:
            Return 204 if delete action is successful. Otherwise the operation
            fails.
        """
        url = self.base_url + cirrus_rest.uri.get('hardware') + '/' + str(sut_id)
        headers = self.headers
        if 'auth' not in self.headers:
            headers['auth'] = self.get_session_id()
        r = requests.delete(url=url, headers=headers, verify=False)
        if r.status_code != 204:
            self.builtin.log_to_console("Deleting HW failed. status code:%s, sut_id:%s" % (r.status_code, sut_id))
            return r.status_code
        else:
            check = requests.get(url=url, headers=headers, verify=False)
            if check.status_code == 200:
                self.builtin.log_to_console("Deleting HW failed. Get HW and HW still exists. status code:%s, sut_id:%s" % (r.status_code, sut_id))
                return r.status_code
        return r.status_code

    def clone_hardware(self, sut_id, attr, attr_value):
        """Clone HW scenario. Use GET/POST REST API to add a HW with data from GET api, and check if
        the modification takes effect.

        Args:
            sut_id: Cirrus HW id that would be cloned from.
            attr: Cirrus HW attribute.
            attr_value: Cirrus HW attribute value.
            
        Returns:
            Return 200 if the actions are successful. Otherwise the operation
            fails.
        """
        url = self.base_url + cirrus_rest.uri.get('hardware') + '/' + str(sut_id)
        headers = self.headers
        if 'auth' not in self.headers:
            headers['auth'] = self.get_session_id()
        r = requests.get(url=url, headers=headers, verify=False)
        if r.status_code != 200:
            self.builtin.log_to_console("Fetching HW failed. status code:%s, sut_id:%s" % (r.status_code, sut_id))
            return r.status_code
        payload = [r.json()]
        payload[0][attr] = attr_value
        payload[0]['name'] =  payload[0]['name'] + '_new'
        payload[0].pop('id')
        data = json.dumps(payload).encode('utf-8')
        clone_hw_url = self.base_url + cirrus_rest.uri.get('hardware')
        r = requests.post(url=clone_hw_url, data=data, headers=headers, verify=False)
        cloned_id = r.json()['hardwareData'][0]['id']
        self.builtin.log_to_console(r.json())
        check_new_url = self.base_url + cirrus_rest.uri.get('hardware') + '/' + str(cloned_id)
        check = requests.get(url=check_new_url, headers=headers, verify=False)
        if check.status_code != 200:
            self.builtin.log_to_console("Adding HW failed. status code:%s, sut_id:%s" % (check.status_code, cloned_id))
            return check.status_code
        else:
            diff = []
            for key in payload[0]:
                if key == 'name' or check.json()[key] == payload[0][key]:
                    continue
                else:
                    self.builtin.log_to_console("Cloned HW data mismatched. Cloned data:%s, Origin data:%s." % (check.json(), payload[0]))
                    return -1
        return r.status_code

    def add_test_plan(self, testplan):
        """Save new test plan in apppliance.

        Args:
            testplan: test plan file path in the execution environment.

        Returns:
            Return 200 if the actions are successful. Otherwise the operation
            fails.
        """
        testplan_name = testplan.split('/')[-1]
        url = self.base_url + cirrus_rest.uri.get('testplan')
        headers = self.headers
        if 'auth' not in self.headers:
            headers['auth'] = self.get_session_id()
        with open(testplan, 'r') as f:
            payload = json.load(f)
        data = json.dumps(payload).encode('utf-8')
        r = requests.post(url=url, data=data, headers=headers, verify=False)
        self.builtin.log_to_console(r.json())
        if r.status_code != 200:
            self.builtin.log_to_console("Saving testplan failed. status code:%s, testplan:%s" % (r.status_code, payload))
            return r.status_code
        return r.status_code

    def compare_test_plan_content(self, testplan_name, expect_content):
        """Get test plan content and comapre it with expected content.

        Args:
            testplan_name: test plan name in appliance.
            expect_content: expected test plan content.

        Returns:
            Return 200 if the actions are successful. Otherwise the operation
            fails.
        """
        url = self.base_url + cirrus_rest.uri.get('testplan') + '/ci/data/cirrus/testplans/' + str(testplan_name)
        headers = self.headers
        if 'auth' not in self.headers:
            headers['auth'] = self.get_session_id()
        r = requests.get(url=url, headers=headers, verify=False)
        if r.status_code != 200:
            self.builtin.log_to_console("Getting testplan content failed. status code:%s, testplan name:%s" % (r.status_code, testplan_name))
            return r.status_code
        with open(expect_content, 'r') as f:
            expect = json.load(f)
        if set(expect) >= set(r.json()):
            message = format_jcf(r.json()) + '\n============' + format_jcf(expect)
            self.builtin.log_to_console("Comparing testplan content failed. mismatches:%s" % message)
            return -1
        return r.status_code

    def edit_test_plan(self, testplan_name, content):
        """Edit test plan content.

        Args:
            testplan: test plan name in appliance.
            content: test plan file path in the execution environment.

        Returns:
            Return 200 if the actions are successful. Otherwise the operation
            fails.
        """
        url = self.base_url + cirrus_rest.uri.get('testplan') + '/ci/data/cirrus/testplans/' + str(testplan_name)
        headers = self.headers
        if 'auth' not in self.headers:
            headers['auth'] = self.get_session_id()
        with open(content, 'r') as f:
            payload = json.load(f)
        data = json.dumps(payload).encode('utf-8')
        self.builtin.log_to_console(data)
        r = requests.put(url=url, data=data, headers=headers, verify=False)
        self.builtin.log_to_console(r.json())
        if r.status_code != 200:
            self.builtin.log_to_console("Editing testplan content failed. status code:%s, testplan name:%s" % (r.status_code, testplan_name))
            return r.status_code
        check = self.compare_test_plan_content(os.path.basename(content), content)
        if check != 200:
            self.builtin.log_to_console("Compare expect testplan content and testplan in Cirrus but data is not the same. status code:%s." % check)
            return check
        return r.status_code

    def submit_test_plan(self, testplan):
        """Submit a test plan. And check job id matches the reg format.

        Args:
            testplan: file that contains test plan contents.

        Returns:
            Return both status code and job id.
            Return status code 200 if the actions are successful. Otherwise the operation
            fails.
        """
        url = self.base_url + cirrus_rest.uri.get('jobs')
        headers = self.headers
        if 'auth' not in self.headers:
            headers['auth'] = self.get_session_id()
        with open(testplan, 'r') as f:
            payload = json.load(f)
        data = json.dumps(payload).encode('utf-8')
        r = requests.post(url=url, data=data, headers=headers, verify=False)
        self.builtin.log_to_console(r.json())
        if r.status_code != 200:
            self.builtin.log_to_console("Submiting job failed. status code:%s, testplan:%s" % (r.status_code, payload))
            return r.status_code
        job_id = r.json()['uri'].split("/")[-1]
        m = re.match('[A-Za-z0-9.-]+_(\\w+)_(\\d+)', job_id)
        if not m:
            self.builtin.log_to_console("Submiting job id does not match. job id: %s" % job_id)
            return -1 
        return r.status_code, job_id

    def check_job_status(self, job_id):
        """Keep on moniotring job status for a specific job id. 
        Monitoring will keep for 3 hours before job status becomes either pass/fail/abort.

        Args:
            job_id: job id.

        Returns:
            Return job status such as 'pass', 'fail', 'abort'.
            Return HTTP status code if fetching job status failed.
        """
        url = self.base_url + cirrus_rest.uri.get('jobs') + '/' + str(job_id)
        headers = self.headers
        if 'auth' not in self.headers:
            headers['auth'] = self.get_session_id()
        r = requests.get(url=url, headers=headers, verify=False)
        if r.status_code != 200:
            self.builtin.log_to_console("Get job status failed. status code:%s. job id:%s." % (r.status_code, job_id))
            return r.status_code
        time_count = 0
        # keep monitoring the job status if the status is queued, running, or aborting until 3 hours pass
        while (r.json()['status'] == 'queued' or r.json()['status'] == 'running' \
                or r.json()['status'] == 'aborting' or r.json()['status'] == 'aborted') and time_count < 2160 :
            time.sleep(5)
            r = requests.get(url=url, headers=headers, verify=False)
            if r.status_code != 200:
                self.builtin.log_to_console("Get job status failed. status code:%s. job id:%s." % (r.status_code, job_id))
                return r.status_code
            time_count = time_count + 1
        status = r.json()['status']
        self.builtin.log_to_console("Get job status:%s." % status)
        return status

    def delete_test_plan(self, testplan_name):
        """Delete a test plan and check if it's still exist or not.

        Args:
            testplan_name: testplan file name to be deleted.

        Returns:
            Return 204 if the actions are successful. Otherwise the operation
            fails.
        """
        url = self.base_url + cirrus_rest.uri.get('testplan') + '/ci/data/cirrus/testplans/' + str(testplan_name)
        headers = self.headers
        if 'auth' not in self.headers:
            headers['auth'] = self.get_session_id()
        r = requests.delete(url=url, headers=headers, verify=False)
        if r.status_code != 204:
            self.builtin.log_to_console("Deleting testplan failed. status code:%s, testplan:%s" % (r.status_code, testplan_name))
            return r.status_code
        else:
            check = requests.get(url=url, headers=headers, verify=False)
            if check.status_code == 200:
                self.builtin.log_to_console("Deleting testplan failed. Get testplan and testplan still exists. status code:%s, testplan:%s" % (r.status_code, testplan_name))
                return r.status_code
        return r.status_code

    def export_hardware(self, hw_id):
        """Export hardware and download the export json file. Then compare if the export file contains correct info.

        Args:
            hw_id: hw id to export.

        Returns:
            Return status code 200 if the actions are successful. Otherwise the operation
            fails.
        """
        url = self.base_url + cirrus_rest.uri.get('export_hardware')
        headers = self.headers
        if 'auth' not in self.headers:
            headers['auth'] = self.get_session_id()
        payload = {"id": [hw_id]}
        data = json.dumps(payload).encode('utf-8')
        r = requests.post(url=url, data=data, headers=headers, verify=False)
        if r.status_code != 200:
            self.builtin.log_to_console("Exporting HW failed. status code:%s, sut id:%s" % (r.status_code, hw_id))
            return r.status_code
        url = self.base_url + cirrus_rest.uri.get('export_hardware') + '/' + r.json()['exportFile']
        r = requests.get(url=url, headers=headers, verify=False)
        if r.status_code != 200:
            self.builtin.log_to_console("Downloading exported HW file failed. status code:%s, file:%s" % (r.status_code, r.json()['exportFile']))
            return r.status_code
        export_content = r.json()
        self.builtin.log_to_console(export_content[0])
        check = self.compare_hardware_content(hw_id, export_content[0])
        if check != 200:
            self.builtin.log_to_console("Compare exported HW file and HW in Cirrus but data is not the same. status code:%s." % check)
            return check
        return r.status_code

    def compare_hardware_content(self, hw_id, export_content):
        """Compare hw data in Cirrus is the same as data in exported file.

        Args:
            hw_id: exported hw id.
            export_content: exported json file content.
                            {'name':'test1','desc':'123'}

        Returns:
            Return status code 200 if the actions are successful. Otherwise the operation
            fails.
        """
        url = self.base_url + cirrus_rest.uri.get('hardware') + '/' + str(hw_id)
        headers = self.headers
        if 'auth' not in self.headers:
            headers['auth'] = self.get_session_id()
        r = requests.get(url=url, headers=headers, verify=False)
        if r.status_code != 200:
            self.builtin.log_to_console("Get HW failed. status code:%s, hw id:%s" % (r.status_code, hw_id))
            return r.status_code
        not_match = []
        for key in export_content:
            if key in r.json() and r.json()[key] == export_content[key] or key == 'sys_password' or key == 'ilo_password' or key == 'id':
                continue
            else:
                not_match.append({key:[r.json()[key],export_content[key]]})
        if not_match:
            self.builtin.log_to_console("Comparing HW content failed. mismatches:%s" % (not_match))
            return -1
        return r.status_code

    def import_hardware(self, import_json_path):
        """Import hardware and compare if the import info are correctly imported to Cirrus.

        Args:
            import_json_path: json file including hw info to be imported.

        Returns:
            Return status code 200 if the actions are successful. Otherwise the operation
            fails.
        """
        url = self.base_url + cirrus_rest.uri.get('import_hardware')
        headers = self.headers
        if 'auth' not in self.headers:
            headers['auth'] = self.get_session_id()
        import_json = import_json_path.split('/')[-1]
        files = {import_json:(open(import_json_path, 'rb'))}
        r = requests.post(url=url, files=files, headers=headers, verify=False)
        if r.status_code != 200:
            self.builtin.log_to_console("Loading import file failed. status code:%s, import file:%s" % (r.status_code, import_json))
            return r.status_code
        url = self.base_url + cirrus_rest.uri.get('add_import_hardware')
        payload = [{'file': r.json()['message'], 'decryption': True}]
        data = json.dumps(payload).encode('utf-8')
        r = requests.post(url=url, data=data, headers=headers, verify=False)
        if r.status_code != 202:
            self.builtin.log_to_console("Importing import file failed. status code:%s, import file:%s" % (r.status_code, import_json))
            return r.status_code
        return r.status_code

    def export_testplan(self, testplan):
        """Export testplan and download the export file. Then compare if the export file contains correct info.

        Args:
            testplan: existing testplan in Cirrus to export.

        Returns:
            Return status code 200 if the actions are successful. Otherwise the operation
            fails.
        """
        url = self.base_url + cirrus_rest.uri.get('export_testplan')
        headers = self.headers
        if 'auth' not in self.headers:
            headers['auth'] = self.get_session_id()
        payload = {"info": [{"name":"/ci/data/cirrus/testplans/" + testplan}]}
        data = json.dumps(payload).encode('utf-8')
        r = requests.post(url=url, data=data, headers=headers, verify=False)
        if r.status_code != 200:
            self.builtin.log_to_console("Exporting testplan failed. status code:%s, testplan:%s" % (r.status_code, testplan))
            return r.status_code
        zip = r.json()['export_testplanFile']
        url = self.base_url + cirrus_rest.uri.get('export_testplan') + '/' + zip
        r = requests.get(url=url, headers=headers, verify=False)
        if r.status_code != 200:
            self.builtin.log_to_console("Downloading exported testplan file failed. status code:%s, file:%s" % (r.status_code, zip))
            return r.status_code
        z = zipfile.ZipFile(StringIO.StringIO(r.content))
        z.extractall()
        download_file = z.namelist()[0]
        check = self.compare_test_plan_content(testplan, download_file)
        if check != 200:
            self.builtin.log_to_console("Compare exported testplan file and testplan in Cirrus but data is not the same. status code:%s." % check)
            return check
        return r.status_code

    def import_testplan(self, import_json_path):
        """Import testplan and compare if the import info are correctly imported to Cirrus.

        Args:
            import_json_path: json file including testplan info to be imported.

        Returns:
            Return status code 200 if the actions are successful. Otherwise the operation
            fails.
        """
        url = self.base_url + cirrus_rest.uri.get('import_testplan')
        import_json = import_json_path.split('/')[-1]
        m = MultipartEncoder(
            fields={'file': (import_json, open(import_json_path, 'rb'), 'application/x-zip-compressed')}
            )
        headers = self.headers
        if 'auth' not in self.headers:
            headers['auth'] = self.get_session_id()
        headers['Content-Type'] = m.content_type
        r = requests.post(url=url, data=m, headers=headers, verify=False)
        if r.status_code != 201:
            self.builtin.log_to_console("Importing import file failed. status code:%s, import file:%s" % (r.status_code, import_json))
            return r.status_code
        return r.status_code

    def backup_cirrus(self):
        """Backup Cirrus data including hardware, testplans, usergroups, config, and reports.

        Args:
            None

        Returns:
            Return status code 200 if the actions are successful. Otherwise the operation
            fails.
        """
        url = self.base_url + cirrus_rest.uri.get('backup_config')
        url = self.base_url + cirrus_rest.uri.get('start_backup')
        return r.status_code

    def restore_cirrus(self):
        """Restore Cirrus data including hardware, testplans, usergroups, and config.

        Args:
            None

        Returns:
            Return status code 200 if the actions are successful. Otherwise the operation
            fails.
        """
        return r.status_code

    def abort_job_gracefully(self, job_id):
        """Abort job gracefully.

        Args:
            job_id: the job id you want to abort. ex: ci-0050568ef079_administrator_25

        Returns:
            Return status code 200 if the actions are successful. Otherwise the operation
            fails.
        """
        url = self.base_url + cirrus_rest.uri.get('jobs') + "/" + str(job_id) + cirrus_rest.uri.get('abort_grace')
        headers = self.headers
        if 'auth' not in self.headers:
            headers['auth'] = self.get_session_id()
        r = requests.delete(url=url, headers=headers, verify=False)
        if r.status_code != 204:
            self.builtin.log_to_console("Aborting job failed. status code:%s, job id:%s" % (r.status_code, job_id))
            return r.status_code
        return r.status_code

    def abort_job_immediately(self, job_id):
        """Abort job immediately.

        Args:
            job_id: the job id you want to abort. ex: ci-0050568ef079_administrator_25

        Returns:
            Return status code 200 if the actions are successful. Otherwise the operation
            fails.
        """
        url = self.base_url + cirrus_rest.uri.get('jobs') + "/" + str(job_id) + cirrus_rest.uri.get('abort_imm')
        headers = self.headers
        if 'auth' not in self.headers:
            headers['auth'] = self.get_session_id()
        r = requests.delete(url=url, headers=headers, verify=False)
        if r.status_code != 204:
            self.builtin.log_to_console("Aborting job failed. status code:%s, job id:%s" % (r.status_code, job_id))
            return r.status_code
        return r.status_code


def format_jcf(value):
    a = json.dumps(value, sort_keys=True, indent=4)
    message = '\n'.join('  ' + line for line in a.splitlines())
    return message
