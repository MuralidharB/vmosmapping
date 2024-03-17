
from flask import render_template, redirect, request, url_for
from apps.vm2tenants import blueprint

@blueprint.route('/', methods=['GET'])
def get_vm2tenants():
    pass
