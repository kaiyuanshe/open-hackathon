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

    function pageLoad() {
        getTalentList().then(function (data) {
            if (data.error) {

            } else {
                $('#talent_list').append($('#talent_list_template').tmpl(data.splice(0, 6)));
            }
        });

        getGrantedawards().then(function (data) {
            if (data.error) {

            } else {
                var infn3 = $('#info3');
                var tabs = infn3.find('.oh-tabs').append($('#award_title_template').tmpl(data));
                infn3.find('.tab-content').append($('#award_list_template').tmpl(data));
                tabs.tab();
                tabs.find('a:eq(0)').trigger('click');
                infn3.find('.carousel').each(function (i, o) {
                    $(o).find('.carousel-indicators>li:eq(0)').addClass('active');
                    $(o).find('.carousel-inner>.item:eq(0)').addClass('active');
                })
                infn3.find('.carousel').carousel();
                infn3.removeClass('hide');
            }
        })

        oh.api.admin.hackathon.notice.list.get({
            
        }, function(data) {
            var tmpl = '<li><a href="{link}">{content}\
                        <span>{update_time}</span></a></li>';

            if(data.length > 0) {
                //order: last, first, second, ..., last, first
                var param = {update_time: moment(data[data.length-1].update_time).format('YYYY-MM-DD'), link: data[data.length-1].link, content: data[data.length-1].content};
                $('.oh-notice-list').append(tmpl.format(param));
                for(var i = 0; i < data.length; ++i) {
                    param = {update_time: moment(data[i].update_time).format('YYYY-MM-DD'), link: data[i].link, content: data[i].content};
                    $('.oh-notice-list').append(tmpl.format(param));
                }
                param = {update_time: moment(data[0].update_time).format('YYYY-MM-DD'), link: data[0].link, content: data[0].content};
                $('.oh-notice-list').append(tmpl.format(param));

                var totoalNoticeCount = data.length;
                var firstNoticeElement = $('.oh-notice-list > li:first');
                var minMarginVal = -40*(totoalNoticeCount+1);
                var maxMarginVal = 0;
                firstNoticeElement.css({"margin-top":  "-40px"});
                
                $('#btn-notice-up').click(function(){
                    firstNoticeElement.stop(true, true).animate({"margin-top": "-=40px"}, 500, function() {
                        var marginVal = parseInt(firstNoticeElement.css("margin-top").slice(0, -2));
                        if(marginVal == minMarginVal) {
                            firstNoticeElement.css({"margin-top": (maxMarginVal-40) + "px"});
                        }
                    });
                });

                $('#btn-notice-down').click(function(){
                    firstNoticeElement.stop(true, true).animate({"margin-top": "+=40px"}, 500, function() {
                        var marginVal = parseInt(firstNoticeElement.css("margin-top").slice(0, -2));
                        if(marginVal == maxMarginVal) {
                            firstNoticeElement.css({"margin-top": (minMarginVal+40) + "px"});
                        }
                    });
                });

                //automacally scrolling notice
                setInterval(function() {
                    firstNoticeElement.stop(true, true).animate({"margin-top": "-=40px"}, 500, function() {
                        var marginVal = parseInt(firstNoticeElement.css("margin-top").slice(0, -2));
                        if(marginVal == minMarginVal) {
                            firstNoticeElement.css({"margin-top": (maxMarginVal-40) + "px"});
                        }
                    });
                }, 5000);
            }
            else { //no notice
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
        return oh.api.grantedawards.get({query: {limit: 4}});
    }

    function init() {
        pageLoad();
        bindEvent();
    }

    $(function () {
        init();
    });

})(window.jQuery, window.oh);
