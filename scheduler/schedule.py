import ConfigParser
import datetime
import json
import os
import re
import time
import uuid

import paramiko
import pasteraw
from pygerrit import rest
from pygerrit.rest import auth


_COMMENT = """
Master Results (sha: {master_sha})
  Token creation
    Requests per second: {master_create_rps}
    Time per request: {master_create_tpr}
  Token validation
    Requests per second: {master_validate_rps}
    Time per request: {master_validate_tpr}
Patch Results:
  Token creation
    Requests per second: {patch_create_rps}
    Time per request: {patch_create_tpr}
  Token validation
    Requests per second: {patch_validate_rps}
    Time per request: {patch_validate_tpr}
"""


class ContainerError(Exception):

    def __init__(self, err_code, error, output):
        print 'Error code: %r' % err_code
        print 'Error: %r' % error
        print 'Output: %r' % output


class PerformanceManager(object):

    def __init__(self, host, user):
        self.client = paramiko.client.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(host, username=user)
        self.paste_client = pasteraw.Client()
        self.container_ip = None

    def get_container_by_name(self, name):
        command = 'lxc list  --format json ' + name
        return self.client.exec_command(command)

    def delete_container_by_name(self, name):
        command = 'lxc delete --force ' + name
        return self.client.exec_command(command)

    def launch_container(self):
        container_name = 'keystone-' + uuid.uuid4().hex
        command = 'lxc launch ubuntu1604 ' + container_name
        stdin, stdout, stderr = self.client.exec_command(command)
        return container_name, stdin, stdout, stderr

    def set_container_ip_by_name(self, name):
        while not self.container_ip:
            stdin, stdout, stderr = self.get_container_by_name(name)
            container = json.loads(stdout.read())
            if container and container[0]['state']:
                addresses = (
                    container[0]['state']['network']['eth0']['addresses']
                )
                for address in addresses:
                    if address['family'] == 'inet':
                        if 'address' in address:
                            self.container_ip = address['address']
                            # NOTE(lbragstad): Setting this and leaving the
                            # function can result in connection refused errors
                            # because even though we have an IP address,
                            # networking might not be up inside the container.
                            # Let's give it a few seconds before returning.
                            time.sleep(5)
                        else:
                            time.sleep(2)

    def _build_container_command(self, command):
        values = {'ip': self.container_ip, 'command': command}
        full_command = "ssh root@%(ip)s '%(command)s'" % values
        return full_command

    def install_container(self):
        print 'installing container'
        # Bootstrap and install keystone on the container.
        com = ('git clone https://github.com/lbragstad/keystone-performance; '
               'cd keystone-performance; bash run_everything.sh')
        command = self._build_container_command(com)
        stdin, stdout, stderr = self.client.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()
        if exit_status != 0:
            raise ContainerError(exit_status, stderr.read(), stdout.read())

    def benchmark_master(self):
        com = ('git ls-remote --heads https://github.com/openstack/keystone |'
               'grep master | cut -f1')
        command = self._build_container_command(com)
        stdin, stdout, stderr = self.client.exec_command(command)
        master_sha = stdout.read().rstrip()[:10]
        print 'benchmarking master (sha: %s)' % master_sha

        com = 'cd keystone-performance; bash benchmark.sh'
        command = self._build_container_command(com)
        stdin, stdout, stderr = self.client.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()
        if exit_status != 0:
            raise ContainerError(exit_status, stderr.read(), stdout.read())
        master_results = stdout.read()
        return (master_sha, master_results)

    def benchmark_change(self, ref):
        # Check out the patch to test from Gerrit.
        com = ('cd keystone-performance; '
               'ansible-playbook -i inventory_localhost --sudo '
               '-e "ref=%s" checkout_change.yml') % ref
        command = self._build_container_command(com)
        stdin, stdout, stderr = self.client.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()
        if exit_status != 0:
            raise ContainerError(exit_status, stderr.read(), stdout.read())

        # Benchmark the change under review.
        print 'benchmarking change'
        com = 'cd keystone-performance; bash benchmark.sh'
        command = self._build_container_command(com)
        stdin, stdout, stderr = self.client.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()
        if exit_status != 0:
            raise ContainerError(exit_status, stderr.read(), stdout.read())
        change_results = stdout.read()
        return change_results


def _sorted_ls(path):
    """Sort the contents of a directory by last modified date.

    :param path: directory path
    :returns: a list of files sorted by their last modified time
    """
    def _get_modified_time(f):
        return os.stat(os.path.join(path, f)).st_mtime
    return list(sorted(os.listdir(path), key=_get_modified_time))


def get_next_change_file():
    """Return a filepath that contains data about the next change to test.

    :returns: the absolute path of a file
    """
    path = '/tmp/perf/'
    changes_to_test = _sorted_ls(path)
    if changes_to_test:
        return os.path.join(path, changes_to_test[0])


def get_requests_per_second(result_data):
    tm = re.compile(r'(\d+\.\d+)')
    section_name = None
    section_value = None
    for line in result_data.split('\n'):
        if line.startswith('Benchmarking ') and line.endswith('...'):
            if section_value:
                yield {section_name: section_value}
            section_name = line[13:-3]
            section_value = None
        elif line.startswith('Requests per second:'):
            section_value = tm.search(line).group()
    if section_name:
        yield {section_name: section_value}


def get_time_per_request(result_data):
    tm = re.compile(r'(\d+\.\d+)')
    section_name = None
    section_value = None
    for line in result_data.split('\n'):
        if line.startswith('Benchmarking ') and line.endswith('...'):
            if section_value:
                yield {section_name: section_value}
            section_name = line[13:-3]
            section_value = None
        elif line.startswith('Time per request:'):
            section_value = tm.search(line).group()
    if section_name:
        yield {section_name: section_value}

if __name__ == '__main__':
    config_parser = ConfigParser.ConfigParser()
    config_parser.read('performance.conf')
    gerrit_user = config_parser.get('global', 'gerrit_user')
    gerrit_password = config_parser.get('global', 'gerrit_password')
    perf_user = config_parser.get('scheduler', 'performance_username')
    perf_host = config_parser.get('scheduler', 'performance_host_ip')

    try:
        next_change_path = get_next_change_file()
        while True:
            if next_change_path:
                with open(next_change_path, 'r') as f:
                    event = json.loads(f.read())
                    if event['type'] == 'change-merged':
                        change_ref = None
                        print 'performance testing merged change %s' % (
                            event['change']['url']
                        )
                    else:
                        change_ref = event['patchSet']['ref']
                        print 'performance testing %s at patch set %s' % (
                            event['change']['url'], event['patchSet']['number']
                        )

                # Establish a connection the with host running performance.
                pm = PerformanceManager(perf_host, perf_user)

                # Launch a new container and wait for it to be assigned an IP.
                container_name, stdin, stdout, stderr = pm.launch_container()
                pm.set_container_ip_by_name(container_name)

                # SSH into the container, install keystone, and benchmark
                try:
                    pm.install_container()
                    master_sha, master_results = pm.benchmark_master()
                    change_results = None
                    if change_ref:
                        change_results = pm.benchmark_change(change_ref)
                except ContainerError as e:
                    print 'something bad happened...'
                    print 'cleaning up and trying again'
                    # FIXME(lbragstad): I'm not sure what the best way to
                    # handle this is without just infinite looping and
                    # hammering a system (maybe that is the best way?).
                    pm.delete_container_by_name(container_name)
                    continue

                master_rps = get_requests_per_second(master_results)
                for value in master_rps:
                    if 'token validation' in value:
                        master_validate_rps = value['token validation']
                    elif 'token creation' in value:
                        master_create_rps = value['token creation']

                master_tpr = get_time_per_request(master_results)
                for value in master_tpr:
                    if 'token validation' in value:
                        master_validate_tpr = value['token validation']
                    elif 'token creation' in value:
                        master_create_tpr = value['token creation']

                timestamp = int(time.time())
                date = datetime.datetime.fromtimestamp(timestamp).strftime(
                    '%Y%m%d%H%M%S'
                )
                results = dict(
                    sha=master_sha,
                    timestamp=timestamp,
                    token_creation=dict(
                        requests_per_second=master_create_rps,
                        time_per_request=master_create_tpr
                    ),
                    token_validation=dict(
                        requests_per_second=master_validate_rps,
                        time_per_request=master_validate_tpr
                    )
                )
                results_directory = '../results/%s/%s' % (
                    master_sha, date
                )
                os.makedirs(results_directory)

                summary_file = os.path.join(
                    results_directory,
                    'summary.json'
                )
                with open(summary_file, 'w') as f:
                    f.write(json.dumps(results))

                results_file = os.path.join(
                    results_directory,
                    'benchmark-results.txt'
                )
                with open(results_file, 'w') as f:
                    f.write(master_results)

                if change_results:
                    patch_rps = get_requests_per_second(change_results)
                    for value in patch_rps:
                        if 'token validation' in value:
                            patch_validate_rps = value['token validation']
                        elif 'token creation' in value:
                            patch_create_rps = value['token creation']

                    patch_tpr = get_time_per_request(change_results)
                    for value in patch_tpr:
                        if 'token validation' in value:
                            patch_validate_tpr = value['token validation']
                        elif 'token creation' in value:
                            patch_create_tpr = value['token creation']

                    # Leave a comment on the review.
                    msg = _COMMENT.format(
                        master_sha=master_sha,
                        master_create_rps=master_create_rps,
                        master_create_tpr=master_create_tpr,
                        master_validate_rps=master_validate_rps,
                        master_validate_tpr=master_validate_tpr,
                        patch_create_rps=patch_create_rps,
                        patch_create_tpr=patch_create_tpr,
                        patch_validate_rps=patch_validate_rps,
                        patch_validate_tpr=patch_validate_tpr
                    )
                    gerrit_auth = auth.HTTPDigestAuth(
                        gerrit_user, gerrit_password
                    )
                    gerrit_client = rest.GerritRestAPI(
                        'https://review.openstack.org/', auth=gerrit_auth
                    )

                    change_id = event['change']['id']
                    rev = event['patchSet']['revision']
                    review = rest.GerritReview(message=msg)
                    gerrit_client.review(change_id, rev, review)
                    print 'commented on %s' % event['change']['url']

                # remove container
                pm.delete_container_by_name(container_name)
                os.remove(next_change_path)
                print 'cleaned up container... ready to test next change'
            else:
                time.sleep(1)
            next_change_path = get_next_change_file()
    except KeyboardInterrupt:
        exit()
