import re
import shutil
import os
import pandas as pd

from flask import render_template, redirect, request, url_for, jsonify
from flask_login import login_required
from apps.flavors import blueprint

from apps.osclient import create_flavors as os_create_flavors
from apps.osclient import get_flavor_map
from oslo_config import cfg

CONF = cfg.CONF

@blueprint.route('/', methods=['GET'])
@login_required
def get_flavors():
    return render_template("home/tbl_flavors.html", segment="flavors")


@blueprint.route('/vms_composition', methods=['GET'])
@login_required
def get_vms_composition():
    flavors = pd.read_csv("data/vmflavors.csv")
    flavors['seqno'] = flavors.index
    flavors = flavors.fillna(value="")
    flavors = flavors.to_dict('records')
    return jsonify({"data": flavors})


@blueprint.route('/recommended', methods=['GET', 'POST'])
@login_required
def get_recommended_flavors():
    if request.method == 'GET':
        if not os.path.exists("data/vmflavors_openstack.csv"):
        
            flavors = pd.read_csv("data/vmflavors.csv")
            potential_flavors = []
            flavorid = 0

            bins = [0, 2,4,8,16,32,64,128]
            labels = bins[1:]
            df1 = pd.cut(flavors['CPUs'], bins=bins, labels=labels)
            cpus = sorted(df1.fillna(value=labels[0]).unique())

            existing_flavors = get_flavor_map()
            for c in cpus:
                dfc = pd.DataFrame(flavors[flavors.CPUs == c])
                bins = [0, 8,16,32,64,128,256,512,1024]
                labels = bins[1:]
                df1 = pd.cut(dfc['Memory'], bins=bins, labels=labels)
                memory = sorted(df1.fillna(value=labels[0]).unique())
                for m in memory:
                    dfm = pd.DataFrame(dfc[dfc.Memory == m])
                    bins = [0, 100,200,300,400,500,600,700,800,900, 1000]
                    labels = bins[1:]
                    df1 = pd.cut(dfm['RootDiskSize'], bins=bins, labels=labels)
                    rootdisks = sorted(df1.fillna(value=labels[0]).unique())
                    for d in rootdisks:
                        found = False
                        for i, fl in existing_flavors.items():
                            if c == fl.vcpus and m == fl.ram and \
                                d == fl.disk and fl.is_public:
                                potential_flavors.append(
                                        {'flavorid': fl.id, 'name': fl.name,
                                         'description': fl.description if hasattr(fl, "description") else "",
                                         'vcpus': fl.vcpus, 'ram': fl.ram,
                                         'swap': fl.swap, 'is_public': fl.is_public,
                                         'disk': fl.disk, 'already_exists': True, "modified": False})
                                found = True
                                break
                        if not found:
                            potential_flavors.append(
                                {'flavorid': flavorid, 'name': 'flavor %d' % flavorid,
                                 'description': 'Flavor  %d' % flavorid,
                                 'vcpus': c, 'ram': m, 'swap': 0, 'is_public': True,
                                 'disk': d, 'already_exists': False, "modified": False})
                        flavorid += 1
                    
            for j, fl in existing_flavors.items():
                found = False
                for pfl in potential_flavors:
                    if fl.id == pfl['flavorid']:
                        found = True
                        break
                if not found:
                    potential_flavors.append(
                        {'flavorid': fl.id, 'name': fl.name,
                         'description': fl.description if hasattr(fl, "description") else "",
                         'vcpus': fl.vcpus, 'ram': fl.ram,
                         'swap': fl.swap, 'is_public': fl.is_public,
                         'disk': fl.disk, 'already_exists': True, "modified": False})
            potential_flavors = pd.DataFrame(potential_flavors)
            potential_flavors.to_csv("data/vmflavors_openstack.csv", index=False)

    if request.method == 'POST':
        try:
            flavors = pd.read_csv("data/vmflavors_openstack.csv").to_dict('records')
            if request.form['action'] == 'edit':
                for key, value in request.form.items():
                    if key == 'action':
                        continue
                    m = re.match(r"data\[(\d+)\]\[(\w+)\]", key)
                    idx, k = int(m.groups()[0]), m.groups()[1]
                    flavors[idx][k] = value
                    flavors[idx]['modified'] = True
                flavors = pd.DataFrame(flavors)
                flavors.to_csv("data/vmflavors_openstack.csv", index=False)
        except Exception as ex:
            return jsonify({"message": str(ex)}), 500 

    flavors = pd.read_csv("data/vmflavors_openstack.csv")
    flavors['seqno'] = flavors.index
    flavors = flavors.fillna(value="")
    flavors = flavors.to_dict('records')
    return jsonify({"data": flavors})


@blueprint.route('/create', methods=['POST'])
@login_required
def create_flavors():
    if not os.path.exists("data/vmflavors_openstack.csv"):
        return jsonify({})

    modified_flavors = pd.read_csv("data/vmflavors_openstack.csv").to_dict('records')
    os_create_flavors(modified_flavors)
    return jsonify({})
