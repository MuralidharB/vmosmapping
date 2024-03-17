
from flask import render_template, redirect, request, url_for
from apps.networks import blueprint

@blueprint.route('/', methods=['GET'])
def get_networks():
    pass

