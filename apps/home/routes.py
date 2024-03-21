# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from flask import render_template, request, jsonify
from flask_login import login_required
from jinja2 import TemplateNotFound

import pandas as pd

from apps.vmware_inventory import discover_vcenter_vms, discover_vcenter_networks
from apps.osclient import get_openstack_tenants

from oslo_config import cfg

CONF = cfg.CONF


@blueprint.route('/index')
@login_required
def index():

    df = pd.read_csv("data/vmflavors.csv")
    payload = {'vms': int(df.Name.count()),
               'memory': int(df.Memory.sum()),
               'storage': int(df.RootDiskSize.sum()),
               'vcpus': int(df.CPUs.sum())}
    os_payload = get_openstack_tenants()    
    os_payload = {'domains': len(os_payload['domains']),
                  'regions': len(os_payload['regions']),
                  'projects': sum([len(d['projects']) for k, d in os_payload['domains'].items()])}
    payload.update(os_payload)
    payload['vc_host'] = CONF.vcenter.host
    payload['vc_admin'] = CONF.vcenter.admin

    payload['os_url'] = CONF.openstack.keystone_url
    payload['os_admin'] = CONF.openstack.admin_user
    payload['os_domain'] = CONF.openstack.admin_domain
    return render_template('home/index.html', segment='index', **payload)


@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None

@blueprint.route('/reload_vcenter', methods=['POST'])
def reload_vcenter():
    try:
        discover_vcenter_vms()
        discover_vcenter_networks()
        df = pd.read_csv("data/vmflavors.csv")
        payload = jsonify({'vms': int(df.Name.count()),
                           'memory': int(df.Memory.sum()),
                           'storage': int(df.RootDiskSize.sum()),
                           'vcpus': int(df.CPUs.sum())})
        return payload
    except Exception as ex:
        print(ex)
        return render_template('home/page-500.html'), 500

@blueprint.route('/reload_openstack', methods=['POST'])
def reload_openstack():
    try:
        os_payload = get_openstack_tenants()    
        return jsonify({'domains': len(os_payload['domains']),
                        'regions': len(os_payload['regions']),
                        'projects': sum([len(d['projects']) for k, d in os_payload['domains'].items()])})
    except Exception as ex:
        return render_template('home/page-500.html'), 500
