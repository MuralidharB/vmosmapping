import re
import os
import pandas as pd

from flask import render_template, redirect, request, url_for, jsonify
from flask_login import login_required

from apps.vm2tenants import blueprint
from apps.osclient import get_openstack_tenants

from oslo_config import cfg

CONF = cfg.CONF

@blueprint.route('/', methods=['GET'])
@login_required
def get_vm2tenants():
    tenants = []
    os_payload = get_openstack_tenants()    
    for did, dval in os_payload['domains'].items():
        for pid, pval in dval['projects'].items():
            tenants.append({'name': pval, "domain_name": dval['name']})

    return render_template('home/tbl_vm2tenants.html', segment='vm2tenants', tenants=tenants)


@blueprint.route('/payload', methods=['GET', 'POST'])
@login_required
def get_vm2tenants_payload():
    if not os.path.exists("data/vminventory_mapping.csv"):
        vms = pd.read_csv("data/vminventory.csv")
        vms_mapping = vms[['Instance UUID', "Tenant"]]
        vms_mapping.to_csv("data/vminventory_mapping.csv")

    if request.method == 'POST':
        vms_mapping = pd.read_csv("data/vminventory_mapping.csv")
        tenants = vms_mapping.to_dict('records')
        for key, value in request.form.items():
            if 'Tenant' in key:
                m = re.match(r"data\[(\d+)\]\[Tenant\]", key)
                idx = int(m.groups()[0])
                tenants[idx]['Tenant'] = value            
        vms_mapping = pd.DataFrame(tenants)
        vms_mapping.to_csv("data/vminventory_mapping.csv") 
    vms = pd.read_csv("data/vminventory.csv")
    vms_mapping = pd.read_csv("data/vminventory_mapping.csv")
    vms['seqno'] = vms.index
    vms = vms.fillna(value="")
    vms['Tenant'] = vms_mapping['Tenant']
    vms = vms.to_dict('records')
    support_matrix = pd.read_csv("data/supportmatrix.csv").to_dict('records')
    for vm in vms:
        found = False
        for s in support_matrix:
            if s['Guest OS'] in vm['Guest']:
                found = True
                break
        if not found:
            vm['supported'] = 'Error'
        else:
            if "%s host" % CONF.migration.hypervisor in s.keys():
                if s["%s host" % CONF.migration.hypervisor].lower() == "supported":
                    vm['supported'] = "Success"
                else:
                    vm['supported'] = "Error"
            else:
                vm['supported'] = "Warning"
                
    return jsonify({"data": vms})
