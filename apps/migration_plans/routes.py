import pandas as pd
from flask import render_template, redirect, request, url_for, jsonify
from flask_login import login_required
from apps.migration_plans import blueprint

@blueprint.route('/', methods=['GET'])
@login_required
def get_migration_plans():
    return render_template('home/tbl_migration_plans.html', segment='migration_plans')
