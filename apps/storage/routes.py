import re
import os
import pandas as pd
from flask import render_template, redirect, request, url_for, jsonify
from flask_login import login_required
from apps.storage import blueprint

from apps.osclient import get_volume_types


@blueprint.route('/', methods=['GET'])
@login_required
def get_storage():
    try:
        return render_template('home/tbl_storage.html',
                               segment='storage')
    except Exception as ex:
        return render_template('home/page-500.html'), 500

@blueprint.route('/datastores', methods=['GET', 'POST'])
@login_required
def get_datastores():
    if request.method == "POST":
        try:
            mapping = pd.read_csv("data/vmdatastores_mapping.csv").to_dict('records')
            if request.form['action'] == 'edit':
                for key, value in request.form.items():
                    if key == 'action':
                        continue
                    m = re.match(r"data\[(\d+)\]\[Volume Type]", key)
                    idx = int(m.groups()[0])
                    mapping[idx]["Volume Type"] = value
                    mapping[idx]['modified'] = True
                mapping = pd.DataFrame(mapping)
                mapping.to_csv("data/vmdatastores_mapping.csv", index=False)
        except Exception as ex:
            return jsonify({"message": str(ex)}), 500 

    datastores = pd.read_csv("data/vmdatastores.csv")
    if not os.path.exists("data/vmdatastores_mapping.csv"):
        mapping = datastores[['URL', 'Volume Type']]
        mapping['modified'] = False
        mapping.to_csv("data/vmdatastores_mapping.csv", index=False)
    volume_types = get_volume_types()
    datastores['seqno'] = datastores.index
    datastores = datastores.fillna(value="")
    datastores = datastores.to_dict('records')
    mapping = pd.read_csv("data/vmdatastores_mapping.csv")
    for ds in datastores:
        url = mapping[mapping['URL'] == ds['URL']]
        if url.empty:
            ds['Volume Type'] = "__DEFAULT__"
        else:
            ds['Volume Type'] = url['Volume Type'].iloc[0]
    return jsonify({"data": datastores,
                    "options": {"Volume Type": [{'label': v['name'], 'value':v['name']} for v in volume_types]}})
