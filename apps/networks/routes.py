import pandas as pd
from flask import render_template, redirect, request, url_for, jsonify
from flask_login import login_required
from apps.networks import blueprint

from apps.osclient import get_openstack_tenants


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


@blueprint.route('/json', methods=['GET'])
@login_required
def get_networks_json():
    networks = pd.read_csv("data/vmnetworks.csv")
    vms = pd.read_csv("data/vminventory.csv")

    networks['DT_RowId'] = networks.index
    networks = networks.to_dict('records')
    for n in networks:
        tenant = vms['Tenant'][vms['Instance UUID'] == n['VM Instance UUID']]
        if tenant.empty:
            n['Tenant'] = "NA"
        else:
            n['Tenant'] = tenant.iloc[0]
        n["Network"] = ""
        n["Subnet"] = ""
    return jsonify({"data": networks})
