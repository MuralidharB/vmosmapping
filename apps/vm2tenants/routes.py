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

@blueprint.route('/payload', methods=['GET'])
@login_required
def get_vm2tenants_payload():
    vms = pd.read_csv("vminventory.csv")
    vms['seqno'] = vms.index
    vms['Tenant'] = "Domain/Tenant"
    vms = vms.fillna(value="")
    vms = vms.to_dict('records')
    return jsonify({"data": vms})
