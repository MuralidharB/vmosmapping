# -*- encoding: utf-8 -*-

from flask import Blueprint

blueprint = Blueprint(
    'migration_plans',
    __name__,
    url_prefix='/migration_plans'
)
