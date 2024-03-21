import re
import shutil
import os
import pandas as pd

from flask import render_template, redirect, request, url_for, jsonify
from flask_login import login_required
from apps.images import blueprint

@blueprint.route('/', methods=['GET'])
@login_required
def get_images():
    return render_template("home/tbl_images.html", segment="images")
