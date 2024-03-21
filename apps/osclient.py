"""Simple Python script for querying the status of P3 instances.

This script assumes that the following Python 2 packages are installed.

    python-openstackclient>=3.12.0

This can be done with the following commands

    virtualenv alaska-venv
    source alaska-venv/bin/activate
    pip install -U pip setuptools
    pip install python-openstackclient

This script assumes that the openstack RC file v3 (downloaded from the
OpenStack Hoirizon dashboard) has been sourced, eg.

    source p3-openrc.sh

"""
from __future__ import print_function
import sys
import os
import time
import datetime
import logging
from collections import defaultdict
from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneclient.v3 import client as keystone_client
from novaclient import client as nova_client
from novaclient import api_versions

from oslo_config import cfg


CONF = cfg.CONF
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)
LOG.addHandler(logging.StreamHandler(sys.stdout))
def get_session():
    """Return keystone session"""

    user_domain = CONF.openstack.admin_domain
    user = CONF.openstack.admin_user
    password = CONF.openstack.admin_password
    project = CONF.openstack.admin_project
    auth_url = CONF.openstack.keystone_url
    verify = CONF.openstack.ssl_verify

    # Create user / password based authentication method.
    # https://goo.gl/VxD2FQ
    auth = v3.Password(user_domain_name=user_domain,
                       project_domain_name=user_domain,
                       username=user,
                       password=password,
                       project_name=project,
                       auth_url=auth_url)

    # Create OpenStack keystoneauth1 session.
    # https://goo.gl/BE7YMt
    sess = session.Session(auth=auth, verify=verify)

    return sess


def get_user_map(keystone):
    """Get map of users from keystone"""

    projects = keystone.projects.list()
    #print(projects)
    users = keystone.users.list()
    #print(users)

    regions = keystone.regions.list()
    #print(regions)
    domains = keystone.domains.list()
    #print(domains)

    usermap = {}
    for u in users:
        usermap[u.id] = u.name
  
    domainmap = {}
    for d in domains:
        domainmap[d.id] = {"name": d.name, 'projects':{}, 'users':{}}

    for p in projects:
        d = domainmap[p.domain_id]
        d['projects'][p.id] = p.name

    for u in users:
        d = domainmap[u.domain_id]
        d['users'][u.id] = u.name

    return regions, domainmap, usermap


def get_flavor_map(nclient=None):
    """Get a map of flavours"""

    if nclient is None:
        sess = get_session()
        nclient = nova_client.Client(version=2, session=sess)

    flavors = {}

    for idx, flavor in enumerate(nclient.flavors.list()):
        flavors[flavor.id] = flavor

    return flavors


def query_servers(nova_client):
    """Query list of servers.

    Returns a dictionary of server dictionaries with the key being the
    server name
    """
    servers = defaultdict()
    for idx, server in enumerate(nova_client.servers.list()):
        server_dict = server.to_dict()
        servers[server.human_id] = server_dict
    return servers


def server_flavour_summary(servers, flavours):
    """Log a summary of servers by flavor."""
    log = logging.getLogger(__name__)
    log.info('Summary (index | flavour | instance count):')
    log.info('-' * 80)
    for idx, flavor_id in enumerate(flavours):
        count = 0
        for key in servers:
            if servers[key]['flavor']['id'] == flavor_id:
                count += 1
        log.info('%03i | %-20s | %i', idx, flavours[flavor_id], count)
    log.info('-' * 80)
    log.info('')


def user_summary(servers, users):
    """Log a summary of the servers by user."""
    log = logging.getLogger(__name__)
    user_info = defaultdict()
    for idx, key in enumerate(servers):
        user_id = servers[key]['user_id']
        if user_id not in users:
            users[user_id] = 'user-{:02d}'.format(len(users))
        if user_id not in user_info:
            user_info[user_id] = defaultdict(count=0, server_ids=[])
        user_info[user_id]['count'] += 1
        user_info[user_id]['server_ids'].append(key)

    log.info('Users (index | user id (short) | user name | instance count):')
    log.info('-' * 80)
    for idx, key in enumerate(user_info):
        count = user_info[key]['count']
        log.info('%03i | %.8s | %-12s | %-3i',
                 idx, key, users[key], count)
        for server in user_info[key]['server_ids']:
            created = time.strptime(servers[server]['created'],
                                    '%Y-%m-%dT%H:%M:%SZ')
            age = time.mktime(time.localtime()) - time.mktime(created)
            age = datetime.timedelta(seconds=age)
            log.debug('    |-> (age: %3id) %-20s', age.days, server)
    log.info('-' * 80)
    log.info('')


def create_flavors(flavors):
    # Get a keystone session.
    sess = get_session()

    # Create a OpenStack nova client.
    # https://goo.gl/ryuyzF
    novaclient = nova_client.Client(version=2, session=sess)
    existing_flavors = get_flavor_map(novaclient)
    supports_description = api_versions.APIVersion('2.55')
    for idx, fl in enumerate(flavors):
        if not fl['modified']:
            continue
        import pdb;pdb.set_trace()
        if fl['flavorid'] in existing_flavors:
             novaclient.flavors.delete(fl['flavorid'])
        if novaclient.flavors.api_version < supports_description:
            novaclient.flavors.create(
                fl['name'], fl['ram'],
                fl['vcpus'], fl['disk'],
                flavorid=fl['flavorid'], is_public=fl['is_public'])
        else:
            novaclient.flavors.create(
                fl['name'], fl['ram'],
                fl['vcpus'], fl['disk'],
                flavorid=fl['flavorid'], is_public=fl['is_public'],
                description=fl['description'])

    return flavors


def get_openstack_tenants():
    """Main function."""
    # Get a keystone session.
    sess = get_session()

    # Create a OpenStack nova client.
    # https://goo.gl/ryuyzF
    nova = nova_client.Client(version=2, session=sess)
    keystone = keystone_client.Client(version=3, session=sess)

    regions, domains, users = get_user_map(keystone)
    flavors = get_flavor_map(nova)
    servers = query_servers(nova)
    server_flavour_summary(servers, flavors)
    user_summary(servers, users)

    return {'domains': domains, "regions": regions}


if __name__ == '__main__':
    get_openstack_tenants()
