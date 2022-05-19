# -*- coding: utf-8 -*-
# @Author  : 袁天琪
from flask import Blueprint
from common.libs.user.Helper import ops_render
route_analyse = Blueprint('analyse_page', __name__)

@route_analyse.route("/index")
def index():
    return ops_render("analyse/index.html")


