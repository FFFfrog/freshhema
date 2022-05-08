# -*- coding: utf-8 -*-
# @Author  : 袁天琪
from web.controllers.api import route_api
from flask import request, jsonify, g
from application import app, db
from common.libs.UrlManager import UrlManager
from common.libs.user.Helper import getCurrentDate
from common.models.member.MemberAddress import MemberAddress


@route_api.route("/analyse/index")
def gaodemap():
    return '你好'
