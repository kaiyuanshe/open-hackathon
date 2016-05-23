# -*- coding: utf-8 -*-
"""
Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
 
The MIT License (MIT)
 
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from hackathon.hmongo.models import *
from hackathon.constants import *
from mongoengine import Q
import uuid
from hackathon.util import *
from bson import *
import hashlib
import xlwt


def export_registered_users(filename, hackathon_name):
    hackathon = Hackathon.objects(name=hackathon_name).no_dereference().first()
    if not hackathon:
        print "hackathon %s cannot be found" % hackathon_name
        return

    gender = {
        -1: "保密",
        0: "女",
        1: "男"
    }
    header = ("用户名",
              "昵称",
              "姓名",
              "Email",
              "手机",
              "登录方式",
              "年龄",
              "地址",
              "QQ",
              "skype",
              "微信",
              "微博")

    # prepare data to write
    data_to_write = [header]
    registers = UserHackathon.objects(hackathon=hackathon, role=HACK_USER_TYPE.COMPETITOR).all()
    for reg in registers:
        user = reg.user
        if not user.emails:
            user.emails = []
        if not user.profile:
            user.profile = UserProfile()

        profile = user.profile
        data_to_write.append((user.name,
                              user.nickname,
                              profile.real_name,
                              ",".join([x.email for x in user.emails]),
                              profile.phone,
                              user.provider,
                              gender.get(profile.gender, "保密"),
                              profile.address,
                              profile.qq,
                              profile.skype,
                              profile.wechat,
                              profile.weibo
                              ))

    # write to new Excel file
    book = xlwt.Workbook(encoding="utf8")
    sheet1 = book.add_sheet('注册用户')
    columns = len(header)
    for row_index in range(len(data_to_write)):
        for column_index in range(columns):
            sheet1.write(row_index, column_index, data_to_write[row_index][column_index])

    # sheet1.flush_row_data()
    book.save(filename)


export_registered_users("user.xls", "ampcamp")
