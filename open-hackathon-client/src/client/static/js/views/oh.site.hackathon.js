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

    function teamsbind(data) {
        for(var index in data) {
            if(!data[index]["logo"]) {
                data[index]["logo"] = null;
            }
        }

        var list = $('#team_list').append($('#team_list_temp').tmpl(data, {
            get_logo: function (logo) {
                return logo ? logo : '/static/pic/team-logo.png';
            },
            get_description: function (description) {
                return (description || '').substr(0, 60);
            },
            get_link: function (id) {
                return '/site/' + hackathon_name + '/team/' + id;
            }
        }));
    }

    function pageLoad() {
        $('[data-loadsrc]').each(function (i, img) {

            var $img = $(img).load(function (e) {
                oh.comm.imgLoad(this);
            })
            $img.attr({src: $img.attr('data-loadsrc')});
        });

        getTeamList().then(function (data) {
            if (data.error) {
                showNoTeam();
            } else if (data.length > 0) {
                $('#team span').text('（' + data.length + '）');
                teamsbind(data);
            } else {
                showNoTeam();
            }
        });

        function getTeamlink(team_id, tag) {
            return '/site/' + hackathon_name + '/team/' + team_id + tag;
        }

        getShowList().then(function (data) {
            if (data.error) {
                noShow();
            } else if (data.length > 0) {
                $('#works span').text('（' + data.length + '）');
                $('#team_show').append($('#show_list_temp').tmpl(data, {
                    getImage: function (uri) {
                        uri = uri || '';
                        var uris = uri.split(',');
                        var image_url = '/static/pic/wutu.jpg';
                        $.each(uris, function (i, o) {
                            var u_t = o.split(':::');
                            if (u_t[1] == '0') {
                                image_url = u_t[0];
                                return;
                            }
                        });
                        return image_url;
                    },
                    getAlt: function (uri, note) {
                        var uris = uri.split(',');
                        var src = note;
                        $.each(uris, function (i, o) {
                            var u_t = o.split(':::');
                            if (u_t[1] == '0' && u_t[0].search('.baidu.com') > -1) {
                                src = '百度图片拒绝外链！';
                                return;
                            }
                        });
                        return src
                    },
                    getlinks: function (works, team_id) {

                        var links = '';
                        $.each(works, function (i, work) {
                            var type = work.type;
                            if (type == 0 && links.search('#works_img') == -1) {
                                links += '<a href="' + getTeamlink(team_id, '#works_img') + '" target="_blank">图片</a>';
                            } else if (type == 1 && links.search('#works_video') == -1) {
                                links += '<a href="' + getTeamlink(team_id, '#works_video') + '" target="_blank">视频</a>';
                            } else if (type == 2 && links.search('#works_code') == -1) {
                                links += '<a href="' + getTeamlink(team_id, '#works_code') + '" target="_blank">源代码</a>';
                            } else if (type >= 3 && type <= 6 && links.search('#works_doc') == -1) {
                                links += '<a href="' + getTeamlink(team_id, '#works_doc') + '" target="_blank">文档</a>';
                            }
                        });
                        return links;
                    },
                    link: function (team_id) {
                        return getTeamlink(team_id, '');
                    }
                }));
            } else {
                noShow();
            }
        });

        getGrantedAwards().then(function(data) {
            if (data.error) {
                console.log(data);
            } else {
                if (data.length == 0)
                    $('#tab_item_awards').hide();

                var awardList = {};
                var awardIdSet = {}; // remove deplicated awards
                for (var index in data) {
                    var award = data[index];
                    if (award.id in awardIdSet)
                        continue;

                    if (award.level in awardList) {
                        awardList[award.level].push(award);
                    } else {
                        awardList[award.level] = [award];
                    }
                    awardIdSet[award.id] = true;
                }

                for (var i=10; i>=0; i--) {
                    if (!(i in awardList))
                        continue;

                    var appendStr = "";
                    appendStr += "<div class='list-group' style='margin-left:40px;width:700px'><a class='list-group-item' style='background-color: #eaeaea'><h4 class='list-group-item-heading'>" + awardList[i][0].name + "</h4></a>";
                    for (var j in awardList[i]) {
                        for (var t in awardList[i][j].team) {
                            appendStr += "<a class='list-group-item' style='padding-left:40px; height:60px' target='_blank' href=/site/" + hackathon_name + "/team/" + awardList[i][j]['team'][t].id + ">"
                            if (awardList[i][j].sub_name)
                                appendStr += "<span class='badge' style='font-weight:bold; font-size:12px'>" + awardList[i][j].sub_name + "</span>";
                            appendStr += "<p class='list-group-item-text'>" + (awardList[i][j]['team'][t].project_name || "项目") + "</p>";
                            appendStr += "<p class='list-group-item-text' style='font-weight:bold'>团队： " + awardList[i][j]['team'][t].name + "</p></a>";
                        }
                    }
                    appendStr += "</div>";

                    $('#team_awards').append(appendStr);
                }
            }
        });

        //get hackathon notice
        oh.api.hackathon.notice.list.get({
            query: {
                hackathon_name: hackathon_name,
                order_by: 'time'
            }
        }, function (data) {
            if (data.error) {
                oh.comm.alert(data.error.message);
            } else if(data.items.length > 0) {
                data = data.items;
                $('#new > span').text('（' + data.length + '）');

                var noticeIconByCategory = {
                    0: 'glyphicon glyphicon-bullhorn', //'黑客松信息'
                    1: 'glyphicon glyphicon-user', //'用户信息'
                    2: 'glyphicon glyphicon-th-list', //'实验信息'
                    3: 'glyphicon glyphicon-gift', //'获奖信息'
                    4: 'glyphicon glyphicon-edit' //'模板信息'
                };

                $('#oh-latest-news').append($('#notice_list_temp').tmpl(data, {
                    getNoticeIcon: function (category) {
                        return noticeIconByCategory[category];
                    },
                    getNoticeTime: function (update_time) {
                        var current_time = new Date().getTime();
                        var time_distance = current_time - update_time;
                        var timing = {year: 0, month: 0, week: 0, day: 0, hour: 0, minute: 0};

                        if (time_distance > 0) {
                            timing.year = Math.floor(time_distance / 86400000 / 365)
                            time_distance -= timing.year * 86400000 * 365;
                            timing.month = Math.floor(time_distance / 86400000 / 30)
                            time_distance -= timing.month * 86400000 * 30;
                            timing.week = Math.floor(time_distance / 86400000 / 7)
                            time_distance -= timing.week * 86400000 * 7;
                            timing.day = Math.floor(time_distance / 86400000)
                            time_distance -= timing.day * 86400000;
                            timing.hour = Math.floor(time_distance / 3600000)
                            time_distance -= timing.hour * 3600000;
                            timing.minute = Math.floor(time_distance / 60000)
                            time_distance -= timing.minute * 60000;
                        }

                        var show_text;
                        if (timing.year > 0)        show_text = timing.year + '年前';
                        else if (timing.month > 0)  show_text = timing.month + '个月前';
                        else if (timing.week > 0)   show_text = timing.week + '周前';
                        else if (timing.day > 0)    show_text = timing.day + '天前';
                        else if (timing.hour > 0)   show_text = timing.hour + '小时前';
                        else if (timing.minute > 5) show_text = timing.minute + '分钟前';
                        else                        show_text = '刚刚'; //less than 5min, show '刚刚'

                        return show_text;
                    }
                }));
            } else {
                noNotice();
            }
        });

        if (window.location.href.search('#') != -1) {
            var tabId = "#tab_" + window.location.href.substring(window.location.href.search('#') + 1);
            $(tabId).trigger('click');
            $('html, body').animate({scrollTop: 0}, 'fast');
        }
    }

    function noNotice() {
        $('#news').append('<div class="col-md-12 text-center no-team">' +
            '亲，暂时没有动态消息的哦～<br/><img src="/static/pic/no-notice.jpg"><div>')
    }

    function noShow() {
        $('#works').append('<div class="col-md-12 text-center no-team"><img  src="/static/pic/no-show.png"><div>')
    }

    function showNoTeam() {
        $('#team_list').append('<div class="col-md-12 text-center no-team"><img  src="/static/pic/no-team.png"><div>')
    }

    function getTeamList() {
        return oh.api.hackathon.team.list.get({header: {hackathon_name: hackathon_name}});
    }

    function getShowList() {
        return oh.api.hackathon.show.list.get({header: {hackathon_name: hackathon_name}})
    }

    function getGrantedAwards() {
        return oh.api.hackathon.grantedawards.get({header: {hackathon_name: hackathon_name}})
    }

    function submitRegister() {
        var regieter_btn = $('a[data-type="register"]').click(function (e) {
            e.preventDefault();
            oh.api.user.registration.post({
                // body: {hackathon_name: hackathon_name},
                header: {hackathon_name: hackathon_name}
            }, function (data) {
                if (data.error) {

                    if (data.error.code == 420) {
                        var confim = $('body').Dialog({
                            title: '提示',
                            body: data.error.friendly_message,
                            footer: [

                                $('<button class="btn btn-warning">取消</button>').click(function (e) {
                                    confim.hide();
                                }),
                                $('<button class="btn btn-primary">切换登录</button>').click(function (e) {
                                    confim.hide();
                                    window.location.href = '/logout?return_url=/login?return_url=' + encodeURIComponent('/site/' + hackathon_name + '&provides=' + data.error.provides);
                                })
                            ],
                            modal: 'confirm'
                        });
                    } else {
                        oh.comm.alert('错误', data.error.friendly_message);
                    }
                } else {
                    var message = $('#status').empty();
                    if (data.status == 0) {
                        message.append('<p>您的报名正在审核中，请等待。</p>');
                    } else if (data.status == 2) {
                        message.append('<p>您的报名已被拒绝，如有疑问请联系主办方。</p>');
                    } else {
                        message.append('<a class="btn btn-primary btn-lg" href="/site/' + hackathon_name + '/settings">立即参加</a>\
                                <p>您的报名已经审核已通过。</p>');
                        window.location.reload();
                    }
                }
            })
        });
    }

    function init() {
        pageLoad();
        submitRegister();
    };

    $(function () {
        init();
    });

})(window.jQuery, window.oh);