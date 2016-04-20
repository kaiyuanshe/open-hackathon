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

    var isProfile = false;
    var user_id = 0;
    var edit_tmpl = '<a class="right btn btn-success btn-sm" href="/user/edit"><i class="fa fa-pencil"></i> 编辑个人资料</a>';

    function getUserProfile(query) {
        return oh.api.user.get(query, function (data) {
            if (!data.error) {
                bingUser(data);
                if (user_id == 0) {
                    $('.user-name').append(edit_tmpl);
                }
                getUserLikeHackathons(query)
            } else {
                if (data.error.code == 404) {

                } else {
                    getUserLikeHackathons(query)
                }
                console.log(data.error);
            }
        });
    }

    function getUserLikeHackathons(data) {
        return oh.api.user.hackathon.like.get(data, function (data) {
            if (!data.error) {
                $('#like_events').append($('#like_event_item').tmpl(data, {
                    get_banner: function (banners) {
                        banners = banners || [];
                        return banners[0] || ''
                    }
                }));
            }
        });
    }

    function getMyEvents() {
        var status_data = {"0": "草稿", "1": "上线", "2": "下线"};
        return oh.api.admin.hackathon.list.get(function (data) {
            var panel = $('#my_events').empty();
            if (!data.error) {
                if (data.length > 0) {
                    panel.append($('#my_event_item').tmpl(data, {
                        get_banner: function (banners) {
                            return banners[0] || ''
                        },
                        get_status: function (status) {
                            return status_data[status];
                        }
                    }));
                } else {
                    panel.append('<h5>没有发布任何活动,<a href="/manage/create_event">发布活动</a></h5>');
                }
            }
        });
    }

    function getMyRegisterEvents(query) {
        return oh.api.user.registration.list.get(query, function (data) {
            var panel = $('#my_register_events').empty()
            if (!data.error) {
                if (data.length > 0) {
                    panel.append($('#my_register_event_item').tmpl(data, {
                        get_banner: function (banners) {
                            banners = banners || [];
                            return banners[0] || '';
                        },
                        get_location: function (location) {
                            return location ? location.substring(0, 5) + (location.length > 5 ? '...' : '') : '在线';
                        }
                    }));
                } else {
                    panel.append('<h5>没有参加过任何活动。。。</h5>');
                }
            }
        });
    }

    function pageload() {
        if (location.pathname.search(/\user\/profile/ig) > -1) {
            user_id = 0;
        } else {
            user_id = location.pathname.replace(/\/user\/p_/ig, '') || 0;
        }
        var query = user_id == 0 ? {} : {query: {user_id: user_id}};
        getUserProfile(query);
        getMyRegisterEvents(query);
        var li = $('a[href="#my_events"]').parents('li');
        var li_join = $('a[href="#my_register_events"]');
        if (user_id == 0) {
            li.removeClass('hide');
            li_join.text('我参与的活动');
            getMyEvents();
        } else {
            li.detach();
            li_join.text('TA参与的活动');
            $('#my_events').detach();
        }

        //choose which panel to open by urlParam
        var active_panel = $.getUrlParam('active_panel') || 0;
        if (active_panel == 1) {
            $('#my_register_events_tab').trigger('click');
        }
        else if (active_panel == 2) {
            $('#my_events_tab').trigger('click');
        }
        else {
            $('#team_works_tab').trigger('click');
        }
    }

    function bingUser(data) {
        var profile = data.profile || {};

        $('.user-name').text(data.nickname);
        $('.user-picture>img').load(function (e) {
            oh.comm.imgLoad(this);
        }).attr({src: profile.avatar_url || data.avatar_url});
        $('.career').html((profile.career_type || '') + '</br>' + (profile.career || ''));
        $('.' + data.provider).addClass('active');
    }

    function init() {
        pageload();
    }

    $(function () {
        init();
    })
})(window.jQuery, window.oh);
