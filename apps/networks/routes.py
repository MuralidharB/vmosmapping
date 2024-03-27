import re
import os
import json
import pandas as pd
from flask import render_template, redirect, request, url_for, jsonify
from flask_login import login_required
from apps.networks import blueprint

from apps.osclient import get_openstack_tenants
from apps.osclient import create_network as os_create_network


@blueprint.route('/', methods=['GET'])
@login_required
def get_networks():
    try:
        tenants = []
        os_payload = get_openstack_tenants()    
        for did, dval in os_payload['domains'].items():
            for pid, pval in dval['projects'].items():
                tenants.append({'name': pval, "domain_name": dval['name']})
        return render_template('home/tbl_networks.html',
                               segment='networks', tenants=tenants)
    except Exception as ex:
        return render_template('home/page-500.html'), 500


@blueprint.route('/json', methods=['GET', 'POST'])
@login_required
def get_networks_json():
    if not os.path.exists("data/vminventory_mapping.csv"):
        vms = pd.read_csv("data/vminventory.csv")
        vms_mapping = vms[['Instance UUID', "Tenant"]]
        vms_mapping.to_csv("data/vminventory_mapping.csv", index=False)

    if request.method == 'POST':
        vms_mapping = pd.read_csv("data/vminventory_mapping.csv")
        networks = pd.read_csv("data/vmnetworks.csv").to_dict('records')
        tenants = vms_mapping.to_dict('records')
        for key, value in request.form.items():
            if 'Tenant' in key:
                m = re.match(r"data\[(\d+)\]\[Tenant\]", key)
                idx = int(m.groups()[0])
                net = networks[idx]
                for t in tenants:
                    if net['VM Instance UUID'] == t['Instance UUID']:
                        t['Tenant'] = value
        vms_mapping = pd.DataFrame(tenants)
        vms_mapping.to_csv("data/vminventory_mapping.csv", index=False) 

    networks = pd.read_csv("data/vmnetworks.csv")
    vms = pd.read_csv("data/vminventory_mapping.csv")

    networks['DT_RowId'] = networks.index
    networks = networks.to_dict('records')
    for net in networks:
        tenant = vms['Tenant'][vms['Instance UUID'] == net['VM Instance UUID']]
        if tenant.empty:
            net['Tenant'] = "NA"
        else:
            net['Tenant'] = tenant.iloc[0]
        net["Network"] = ""
        net["Subnet"] = ""
    return jsonify({"data": networks})


@blueprint.route('/create', methods=['POST'])
@login_required
def create_network():
    params = json.loads(request.data.decode())
    dname = params['tenant'].split("/")[0].strip()
    pname = params['tenant'].split("/")[1].strip()

    network = os_create_network(params['name'], params['description'],
                             None, None, None,
                             dname, pname)
