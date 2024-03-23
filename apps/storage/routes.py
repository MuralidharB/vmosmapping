import pandas as pd
from flask import render_template, redirect, request, url_for, jsonify
from flask_login import login_required
from apps.storage import blueprint

from apps.osclient import get_volume_types


@blueprint.route('/', methods=['GET'])
@login_required
def get_storage():
    try:
        volumetypes = get_volume_types()
        return render_template('home/tbl_storage.html',
                               segment='storage', volumetypes=volumetypes)
    except Exception as ex:
        return render_template('home/page-500.html'), 500

@blueprint.route('/datastores', methods=['GET', 'POST'])
@login_required
def get_datastores():
    datastores = pd.read_csv("data/vmdatastores.csv")
    volume_types = get_volume_types()
    datastores['seqno'] = datastores.index
    datastores = datastores.fillna(value="")
    datastores = datastores.to_dict('records')
    for ds in datastores:
        ds['volumetypes'] = [v['name'] for v in volume_types]
    return jsonify({"data": datastores})
