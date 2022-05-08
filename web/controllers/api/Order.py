# -*- coding: utf-8 -*-
# @Author  : 袁天琪
from web.controllers.api import route_api
from flask import request, jsonify, g
from application import app, db
import json, decimal
from common.models.food.Food import Food
from common.models.pay.PayOrder import PayOrder
from common.models.pay.PayOrderItem import PayOrderItem
from common.libs.UrlManager import UrlManager
from common.libs.user.Helper import selectFilterObj, getCurrentDate, getDictFilterField
from common.libs.pay.PayService import PayService
from common.libs.member.CartService import CartService
from common.models.member.MemberAddress import MemberAddress
from common.models.member.OauthMemberBind import OauthMemberBind
import datetime


@route_api.route("/order/info", methods=["POST"])
def orderInfo():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values
    params_goods = req['goods'] if 'goods' in req else None
    member_info = g.member_info
    params_goods_list = []
    if params_goods:
        params_goods_list = json.loads(params_goods)

    food_dic = {}
    for item in params_goods_list:
        food_dic[item['id']] = item['number']

    food_ids = food_dic.keys()
    food_list = Food.query.filter(Food.id.in_(food_ids)).all()
    data_food_list = []
    yun_price = pay_price = decimal.Decimal(0.00)
    if food_list:
        for item in food_list:
            tmp_data = {
                "id": item.id,
                "name": item.name,
                "price": str(item.price),
                'pic_url': UrlManager.buildImageUrl(item.main_image),
                'number': food_dic[item.id]
            }
            pay_price = pay_price + item.price * int(food_dic[item.id])
            data_food_list.append(tmp_data)

    # 获取地址
    address_info = MemberAddress.query.filter_by(is_default=1, member_id=member_info.id, status=1).first()
    default_address = ''
    if address_info:
        default_address = {
            "id": address_info.id,
            "name": address_info.nickname,
            "mobile": address_info.mobile,
            "address": "%s%s%s%s" % (
                address_info.province_str, address_info.city_str, address_info.area_str, address_info.address)
        }

    resp['data']['food_list'] = data_food_list
    resp['data']['pay_price'] = str(pay_price)
    resp['data']['yun_price'] = str(yun_price)
    resp['data']['total_price'] = str(pay_price + yun_price)
    resp['data']['default_address'] = default_address
    return jsonify(resp)


@route_api.route("/order/create", methods=["POST"])
def orderCreate():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values
    type = req['type'] if 'type' in req else ''
    note = req['note'] if 'note' in req else ''
    express_address_id = int(req['express_address_id']) if 'express_address_id' in req and req[
        'express_address_id'] else 0
    params_goods = req['goods'] if 'goods' in req else None

    items = []
    if params_goods:
        items = json.loads(params_goods)

    if len(items) < 1:
        resp['code'] = -1
        resp['msg'] = "下单失败：没有选择商品~~"
        return jsonify(resp)

    address_info = MemberAddress.query.filter_by(id=express_address_id).first()
    if not address_info or not address_info.status:
        resp['code'] = -1
        resp['msg'] = "下单失败：快递地址不对~~"
        return jsonify(resp)

    member_info = g.member_info
    target = PayService()
    params = {}
    params = {
        "note": note,
        'express_address_id': address_info.id,
        'express_info': {
            'mobile': address_info.mobile,
            'nickname': address_info.nickname,
            "address": "%s%s%s%s" % (
                address_info.province_str, address_info.city_str, address_info.area_str, address_info.address)
        }
    }
    resp = target.createOrder(member_info.id, items, params)
    # 如果是来源购物车的，下单成功将下单的商品去掉
    if resp['code'] == 200 and type == "cart":
        CartService.deleteItem(member_info.id, items)

    return jsonify(resp)


@route_api.route("/order/pay", methods=["POST"])
def orderPay():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    member_info = g.member_info
    req = request.values
    prevpage = ''
    if 'order_sn' in req:
        prevpage = req['prevpage']  # pages/my/index
        order_sn = req['order_sn']
        pay_order_info = PayOrder.query.filter_by(order_sn=order_sn).first()
        # pay_order_info = PayOrder.query.filter_by( order_sn = order_sn,member_id = member_info.id ).first()
        if not pay_order_info:
            resp['code'] = -1
            resp['msg'] = "系统繁忙。请稍后再试1~~"
            return jsonify(resp)

        oauth_bind_info = OauthMemberBind.query.filter_by(member_id=member_info.id).first()
        if not oauth_bind_info:
            resp['code'] = -1
            resp['msg'] = "系统繁忙。请稍后再试2~~"
            return jsonify(resp)

        target_pay = PayService()
        target_pay.orderSuccess(pay_order_id=pay_order_info.id)
        return jsonify(resp)
    else:
        prevpage = json.loads(list(req.to_dict().keys())[0])['prevpage']  # pages/food/index
        food_id = json.loads(list(req.to_dict().keys())[0])['goods'][0]['id']  # int型
        number = json.loads(list(req.to_dict().keys())[0])['goods'][0]['number']  # int型
        if food_id < 1 or number < 1:
            resp['code'] = -1
            resp['msg'] = "购买失败-1~~"
            return jsonify(resp)
        food_info = Food.query.filter_by(id=food_id).first()
        if not food_info:
            resp['code'] = -1
            resp['msg'] = "购买失败-3~~"
            return jsonify(resp)

        if food_info.stock < number:
            resp['code'] = -1
            resp['msg'] = "购买失败,库存不足~~"
            return jsonify(resp)
        return jsonify(resp)


@route_api.route("/order/ops", methods=["POST"])
def orderOps():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values
    member_info = g.member_info
    order_sn = req['order_sn'] if 'order_sn' in req else ''
    act = req['act'] if 'act' in req else ''
    pay_order_info = PayOrder.query.filter_by(order_sn=order_sn, member_id=member_info.id).first()
    if not pay_order_info:
        resp['code'] = -1
        resp['msg'] = "系统繁忙。请稍后再试~~"
        return jsonify(resp)

    if act == "cancel":
        target_pay = PayService()
        ret = target_pay.closeOrder(pay_order_id=pay_order_info.id)
        if not ret:
            resp['code'] = -1
            resp['msg'] = "系统繁忙。请稍后再试~~"
            return jsonify(resp)
    elif act == "confirm":
        pay_order_info.express_status = 1
        pay_order_info.updated_time = getCurrentDate()
        db.session.add(pay_order_info)
        db.session.commit()

    return jsonify(resp)


@route_api.route("/order/cancelled")
def orderCancelled():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values
    member_info = g.member_info
    # 待付款的订单
    query = PayOrder.query.filter_by(member_id=member_info.id, status=-8).all()
    # data_pay_order_list = []
    if query:
        print('12')
        # pay_order.id    [54, 55, 56]
        pay_order_ids = selectFilterObj(query, "id")
        # print(str(pay_order_ids))
        # print('23')
        # pay_order_item.pay_order_id里有pay_order.id的      [<PayOrderItem 57>, <PayOrderItem 58>, <PayOrderItem 59>]
        pay_order_item_list = PayOrderItem.query.filter(PayOrderItem.pay_order_id.in_(pay_order_ids)).all()
        # print(str(pay_order_item_list))
        # print('34')
        # pay_order_item.pay_order_id对应的food_id    [13, 1, 6]
        food_ids = selectFilterObj(pay_order_item_list, "food_id")
        # print(str(food_ids))
        # print('45')
        # 过期时间   [datetime.datetime(2022, 5, 6, 11, 30, 19), datetime.datetime(2022, 5, 6, 22, 30, 38), datetime.datetime(2022, 5, 6, 22, 31, 1)]
        deadline = selectFilterObj(pay_order_item_list, "deadline")
        # print(str(deadline))
        # print('56')
        for i in range(len(deadline)):
            time = getCurrentDate()
            result = deadline[i].__le__(time)
            print(result)
            if result == True:
                ls = []
                ls.append(deadline[i])
                # pay_order_item.pay_order_id里有pay_order.id的
                list1 = PayOrderItem.query.filter(PayOrderItem.pay_order_id.in_(pay_order_ids),
                                                  PayOrderItem.deadline.in_(ls)).all()
                # print(list1)
                # print('1234')
                # pay_order_item里对应的pay_order_id
                list2 = selectFilterObj(list1, "pay_order_id")
                # print(list2)
                # print('12345')
                target_pay = PayService()
                for j in list2:
                    ret = target_pay.closeOrder(pay_order_id=j)
                    if not ret:
                        resp['code'] = -1
                        resp['msg'] = "系统繁忙。请稍后再试~~"
                        return jsonify(resp)
    return jsonify(resp)
