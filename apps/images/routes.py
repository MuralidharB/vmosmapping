import re
import shutil
import os
import pandas as pd

from flask import render_template, redirect, request, url_for, jsonify
from flask_login import login_required
from apps.images import blueprint

from apps.osclient import get_image_list as get_glance_images

@blueprint.route('/', methods=['GET'])
@login_required
def get_images():
    return render_template("home/tbl_images.html", segment="images")

@blueprint.route('/list', methods=['GET', 'POST'])
@login_required
def get_image_list():

    if request.method == 'POST':
        try:
            import pdb;pdb.set_trace()
            if request.form['action'] == 'edit':
                for key, value in request.form.items():
                    if key == 'action':
                        continue
                    m = re.match(r"data\[(\d+)\]\[boot_option]", key)
                    if m:
                        # Update boot options
                        idx = int(m.groups()[0])
                    else:
                        # Update qemu guest agent flags
                        m = re.match(r"data\[(\d+)\]\[qemu_agent]", key)
                        idx = int(m.groups()[0])
        except Exception as ex:
            return jsonify({"message": str(ex)}), 500 

    images = get_glance_images()
    images = pd.DataFrame(images)
    images['seqno'] = images.index
    images = images.to_dict('records')
    return jsonify({"data": images,
                    "options":
                         { "boot_option": [{"label": "UEFI", "value": "UEFI"},
                                            {"label": "BIOS", "value": "BIOS"}],
                           "qemu_agent": [{"label": "yes", "value": "yes"},
                                          {"label": "no", "value": "no"}]}})
