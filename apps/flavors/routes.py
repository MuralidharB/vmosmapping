
from flask import render_template, redirect, request, url_for
from apps.flavors import blueprint

@blueprint.route('/', methods=['GET'])
def get_flavors():
    import pdb;pdb.set_trace()
    pass
