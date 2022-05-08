# -*- coding: utf-8 -*-
# @Author  : 袁天琪
from flask import Blueprint, request, redirect, jsonify
from common.libs.user.Helper import ops_render
from application import app, db

route_analyse = Blueprint('analyse_page', __name__)


@route_analyse.route("/index")
def index():
    return ops_render("analyse/index.html")


@route_analyse.route("/line")
def line():
    return ops_render("analyse/line.html")
