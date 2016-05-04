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


    function getTeamlink(hackathon_name, team_id, tag) {
        return '/site/' + hackathon_name + '/team/' + team_id + tag;
    }

    function pageLoad() {
        getTalentList().then(function (data) {
            if (data.error) {

            } else {
                $('#talent_list').append($('#talent_list_template').tmpl(data.splice(0, 6), {
                    getCareertype: function (data) {
                        return (data.profile || {}).career_type || '';
                    }
                }));
            }
        });

        $('#carousel-example-generic').on('slide.bs.carousel', function (e) {
            carouselright.find('.item').removeClass('active');
            carouselright.find('.item').eq($(e.relatedTarget).index()).addClass('active');
        })
        var carouselright = $('.carousel-right').on('click', '.item', function (e) {
            var nub = $(this).data('slide-to');
            carouselright.find('.item').removeClass('active');
            $(this).addClass('active');
            $('#carousel-example-generic').carousel(nub);
        });
        getGrantedawards().then(function (data) {
            if (data.error) {

            } else {
                $('#award').append($('#award_list_template').tmpl(data, {
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
                    getlinks: function (name, works, team_id) {

                        var links = '';
                        $.each(works, function (i, work) {
                            var type = work.type;
                            if (type == 0 && links.search('#works_img') == -1) {
                                links += '<a href="' + getTeamlink(name, team_id, '#works_img') + '" target="_blank">图片</a>';
                            } else if (type == 1 && links.search('#works_video') == -1) {
                                links += '<a href="' + getTeamlink(name, team_id, '#works_video') + '" target="_blank">视频</a>';
                            } else if (type == 2 && links.search('#works_code') == -1) {
                                links += '<a href="' + getTeamlink(name, team_id, '#works_code') + '" target="_blank">源代码</a>';
                            } else if (type >= 3 && type <= 6 && links.search('#works_doc') == -1) {
                                links += '<a href="' + getTeamlink(name, team_id, '#works_doc') + '" target="_blank">文档</a>';
                            }
                        });
                        return links;
                    },
                    link: function (name, team_id) {
                        return getTeamlink(name, team_id, '');
                    }
                }));
            }
        });

        oh.api.hackathon.notice.list.get({
            query: {
                order_by: 'time',
                page: 1,
                per_page: 6 //the latest 6 notices are shown
            }
        }, function (data) {
            if (data.error) {
                // oh.comm.alert(data.error.message);
            } else if (data.items.length > 0) {
                data = data.items;
                //order: last', first, second, ..., last, first'
                //rolling loop, if it reaches last'/first', moves to last/first
                $('.oh-notice-list').append($('#notice_list_template').tmpl([].concat(data[data.length - 1], data, data[0])));

                var totoalNoticeCount = data.length;
                var firstNotice = $('.oh-notice-list > li:first');
                var noticeHeight = 40;
                var minMarginTopVal = -noticeHeight * (totoalNoticeCount + 1);
                var maxMarginTopVal = 0;
                firstNotice.css({"margin-top": "-" + noticeHeight + "px"});

                $('#btn-notice-up').click(function () {
                    firstNotice.stop(true, true).animate({"margin-top": "-=" + noticeHeight + "px"}, 500, function () {
                        var marginVal = parseInt(firstNotice.css("margin-top").slice(0, -2));
                        if (marginVal == minMarginTopVal) {
                            firstNotice.css({"margin-top": (maxMarginTopVal - noticeHeight) + "px"});
                        }
                    });
                });

                $('#btn-notice-down').click(function () {
                    firstNotice.stop(true, true).animate({"margin-top": "+=" + noticeHeight + "px"}, 500, function () {
                        var marginVal = parseInt(firstNotice.css("margin-top").slice(0, -2));
                        if (marginVal == maxMarginTopVal) {
                            firstNotice.css({"margin-top": (minMarginTopVal + noticeHeight) + "px"});
                        }
                    });
                });

                // automatically rolling notice
                setInterval(function () {
                    $('#btn-notice-up').trigger('click');
                }, 5000);

            } else { //no notice
                $('.oh-notice-list').append("<li>无</li>");
                $('#btn-notice-up').css("display", "none");
                $('#btn-notice-down').css("display", "none");
            }
        });

    }

    function bindEvent() {

    }

    function getTalentList() {
        return oh.api.talent.list.get();
    }

    function getGrantedawards() {
        return oh.api.grantedawards.get({query: {limit: 6}});
    }

    function init() {
        pageLoad();
        bindEvent();
    }

    $(function () {
        init();
    });

})(window.jQuery, window.oh);
