import urllib
import pandas as pd

from flask import render_template, redirect, request, url_for, jsonify
from flask_login import login_required
from apps.migration_plans import blueprint

from apps.osclient import get_openstack_tenants


@blueprint.route('/', methods=['GET'])
@login_required
def get_migration_plans():
    try:
        tenants = []
        os_payload = get_openstack_tenants()    
        for did, dval in os_payload['domains'].items():
            for pid, pval in dval['projects'].items():
                tenants.append({'name': pval, "domain_name": dval['name']})
        return render_template('home/tbl_migration_plans.html',
                               segment='migration_plans', tenants=tenants)
    except Exception as ex:
        return render_template('home/page-500.html'), 500


@blueprint.route('/tenant_vms', methods=['GET'])
@login_required
def tenant_vms():
    tenant_name = urllib.parse.parse_qs(request.query_string.decode())['tenant_name'][0]
    domain_name = urllib.parse.parse_qs(request.query_string.decode())['domain_name'][0]
    vms = pd.read_csv("data/vminventory.csv")
    vms = vms.loc[vms['Tenant'] == "%s/%s" % (domain_name, tenant_name)]
    vms['seqno'] = vms.index
    vms = vms.fillna(value="")
    vms = vms.to_dict('records')
    return jsonify({"data": vms})
