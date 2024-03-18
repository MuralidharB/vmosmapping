import pandas as pd

from flask import render_template, redirect, request, url_for
from flask_login import login_required
from apps.vm2tenants import blueprint

from oslo_config import cfg

CONF = cfg.CONF

@blueprint.route('/', methods=['GET'])
@login_required
def get_vm2tenants():

    vms = pd.read_csv("vminventory.csv").to_dict('records')
    return render_template('home/tbl_vm2tenants.html', segment='index', vms=vms)
