import urllib
import pandas as pd

from flask import render_template, redirect, request, url_for, jsonify
from flask_login import login_required
from apps.migration_plans import blueprint

from apps.osclient import get_openstack_tenants, get_migration_plans
from apps.osclient import get_migration_plans as os_get_migration_plans


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

    #migration_plans = os_get_migration_plans(tenant_name, domain_name)
    vms_mapping = pd.read_csv("data/vminventory_mapping.csv")
    vms = pd.read_csv("data/vminventory.csv")
    vms['seqno'] = vms.index
    vms_mapping.index = vms_mapping["Instance UUID"]
    vms.index = vms_mapping["Instance UUID"]
    vms['Migration Plan'] = ""
    vms['Tenant'] = vms_mapping.Tenant
    vms = vms.loc[vms['Tenant'] == "%s/%s" % (domain_name, tenant_name)]
    vms = vms.fillna(value="")
    vms = vms.to_dict('records')
    return jsonify({"data": vms})
