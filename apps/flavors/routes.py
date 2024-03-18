import pandas as pd

from flask import render_template, redirect, request, url_for
from flask_login import login_required
from apps.flavors import blueprint

from oslo_config import cfg

CONF = cfg.CONF

@blueprint.route('/', methods=['GET'])
@login_required
def get_flavors():
    flavors = pd.read_csv("vmflavors.csv").to_dict('records')
    return render_template('home/tbl_flavors.html', segment='index', flavors=flavors)
