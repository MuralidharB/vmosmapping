import pandas as pd

from flask import render_template, redirect, request, url_for
from flask_login import login_required
from apps.flavors import blueprint

from oslo_config import cfg

CONF = cfg.CONF

@blueprint.route('/', methods=['GET'])
@login_required
def get_flavors():
    flavors = pd.read_csv("vmflavors.csv")

    potential_flavors = []
    flavorid = 0

    bins = [0, 2,4,8,16,32,64,128]
    labels = bins[1:]
    df1 = pd.cut(flavors['CPUs'], bins=bins, labels=labels)
    cpus = sorted(df1.fillna(value=labels[0]).unique())

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
                potential_flavors.append(
                    {'flavorid': flavorid, 'name': 'flavor %d' % flavorid,
                     'description': 'Flavor  %d' % flavorid,
                     'vcpus': c, 'ram': m, 'swap': 0, 'is_public': True,
                     'disk': d})
                flavorid += 1
    return render_template('home/tbl_flavors.html', segment='index', 
                           flavors=flavors.to_dict('records'),
                           potential_flavors=potential_flavors)
