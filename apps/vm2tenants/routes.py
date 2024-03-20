import re
import pandas as pd

from flask import render_template, redirect, request, url_for, jsonify
from flask_login import login_required
from apps.vm2tenants import blueprint

from oslo_config import cfg

CONF = cfg.CONF

@blueprint.route('/', methods=['GET'])
@login_required
def get_vm2tenants():
    return render_template('home/tbl_vm2tenants.html', segment='vm2tenants')

@blueprint.route('/payload', methods=['GET', 'POST'])
@login_required
def get_vm2tenants_payload():
    if request.method == 'POST':
        vms = pd.read_csv("vminventory.csv")
        tenants = vms.Tenant
        for key, value in request.form.items():
            if 'Tenant' in key:
                m = re.match(r"data\[(\d+)\]\[Tenant\]", key)
                print(m.groups())
                idx = int(m.groups()[0])
                tenants[idx] = value            
        vms['Tenant'] = tenants
        vms.to_csv("vminventory.csv") 
    vms = pd.read_csv("vminventory.csv")
    vms['seqno'] = vms.index
    vms = vms.fillna(value="")
    vms = vms.to_dict('records')
    return jsonify({"data": vms})
