# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
import sys

from   flask_migrate import Migrate
from   flask_minify  import Minify
from   sys import exit

from apps.config import config_dict
from apps import create_app

from oslo_config import cfg

# WARNING: Don't run with debug turned on in production!
DEBUG = (os.getenv('DEBUG', 'False') == 'True')

# The configuration
get_config_mode = 'Debug' if DEBUG else 'Production'

# Define an option group
vcenter = cfg.OptGroup('vcenter')

# Define a couple of options
opts = [cfg.StrOpt('host'),
        cfg.StrOpt('admin'),
        cfg.StrOpt('password'),
        cfg.BoolOpt('ssl_verify', default=False)]

# Register your config group
cfg.CONF.register_group(vcenter)

# Register your options within the config group
cfg.CONF.register_opts(opts, group=vcenter)

openstack = cfg.OptGroup('openstack')

# Define a couple of options
opts = [cfg.StrOpt('keystone_url'),
        cfg.StrOpt('admin_user'),
        cfg.StrOpt('admin_password'),
        cfg.StrOpt('admin_project'),
        cfg.StrOpt('admin_domain'),
        cfg.StrOpt('region_name'),
        cfg.BoolOpt('ssl_verify', default=False)]

# Register your config group
cfg.CONF.register_group(openstack)

# Register your options within the config group
cfg.CONF.register_opts(opts, group=openstack)

try:

    # Load the configuration using the default values
    app_config = config_dict[get_config_mode.capitalize()]

except KeyError:
    exit('Error: Invalid <config_mode>. Expected values [Debug, Production] ')

app = create_app(app_config)

if not DEBUG:
    Minify(app=app, html=True, js=False, cssless=False)
    
if DEBUG:
    app.logger.info('DEBUG            = ' + str(DEBUG)             )
    app.logger.info('Page Compression = ' + 'FALSE' if DEBUG else 'TRUE' )
    app.logger.info('DBMS             = ' + app_config.SQLALCHEMY_DATABASE_URI)
    app.logger.info('ASSETS_ROOT      = ' + app_config.ASSETS_ROOT )

if __name__ == "__main__":
    cfg.CONF(["--config-file", "vmosmapping.conf"])
    app.run(host="0.0.0.0")
