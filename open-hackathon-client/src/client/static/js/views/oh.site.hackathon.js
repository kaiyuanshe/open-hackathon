/*
 * Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
 *
 * The MIT License (MIT)
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

(function ($, oh) {
    'use strict';

    var hackathon_name = oh.comm.getCurrentHackathon();

    function pageLoad() {
        oh.api.hackathon.registration.list.get({header: {hackathon_name: hackathon_name}}, function (data) {
            if (data.error) {
                // todo 'Response hackathon register list error'
            } else {
                $('#users').prepend($('#register_list_temp').tmpl(data));
            }
        })
    }

    function submintRegister() {
        var regieter_btn =  $('a[data-type="register"]').click(function (e) {
            e.preventDefault();
            oh.api.user.registration.post({
                header: {hackathon_name: hackathon_name}
            }, function (data) {
                if (data.error) {
                    oh.comm.alert('错误', data.error.friendly_message);
                } else {
                    var message = $('#status').empty();
                    if (data.register.status == 0) {
                        message.append('<p>您的报名正在审核中，请等待。</p>');
                    } else if (data.register.status == 2) {
                        message.append('<p>您的报名已被拒绝，如有疑问请联系主办方。</p>');
                    } else if(data.hackahton_basic_info.freedom_team){
                       message.append('<a class="btn btn-primary btn-lg" href="/site/' + hackathon_name + '/team">立即参加</a>\
                                <p>您的报名已经审核已通过,您可以创建自己的团队或者加入已有的团队。</p>');
                    } else {
                          message.append('<a class="btn btn-primary btn-lg" href="/site/' + hackathon_name + '/settings">立即参加</a>\
                                <p>您的报名已经审核已通过。</p>');
                    }
                }
            })
        });
    }

    function init() {
        pageLoad();
        submintRegister();
    };

    $(function () {
        init();
    });

})(window.jQuery, window.oh);