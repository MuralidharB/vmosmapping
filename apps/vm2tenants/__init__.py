# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import Blueprint

blueprint = Blueprint(
    'vm2tenants_mapping',
    __name__,
    url_prefix='/vm2tenants'
)
