import pandas as pd
from flask import render_template, redirect, request, url_for, jsonify
from flask_login import login_required
from apps.networks import blueprint

@blueprint.route('/', methods=['GET'])
@login_required
def get_networks():
    return render_template('home/tbl_networks.html', segment='networks')

@blueprint.route('/json', methods=['GET'])
@login_required
def get_networks_json():
    networks = pd.read_csv("data/vmnetworks.csv")
    networks['DT_RowId'] = networks.index
    networks = networks.to_dict('records')
    return jsonify({"data": networks})
