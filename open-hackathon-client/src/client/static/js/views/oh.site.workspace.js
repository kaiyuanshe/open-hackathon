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
    var def_expid = 0;

    function pageload() {
        def_expid = $('[data-experiment]').data('experiment') || 0;
        if (def_expid) {
            getExperiment()
        } else {
            getTemplate();
        }
        teamMember();
        hacakthonStat();
    }

    function teamMember() {
        oh.api.user.team.member.get({header: {hackathon_name: hackathon_name}}, function (data) {
            // todo 'Response team member'
            if (data.error) {

            } else {

            }
        });
    }

    function hacakthonStat() {
        oh.api.hackathon.stat.get({
            header: {hackathon_name: hackathon_name}
        }, function (data) {
            $('#online').text(data.online);
            $('#total').text(data.total);
            setTimeout(hacakthonStat(), 60000)
        });
    }

    function getTemplate() {
        oh.api.hackathon.template.get({header: {hackathon_name: hackathon_name}}, function (data) {
            if (data.error) {
                showErrorMsg(data);
            } else {
                if (data.length > 0) {
                    def_expid = data[0].id;
                    postTemplate(data[0].name);
                } else {
                    showErrorMsg({
                        error: {
                            code: 404,
                            friendly_message: '没有模板'
                        }
                    });
                }
            }
        });
    }

    function postTemplate(name) {
        oh.api.user.experiment.post({
            body: {template_name: name, hackathon: hackathon_name}
        }, function (data) {
            loadExperiment(data);
        });
    }

    function showErrorMsg(data) {
        $('#load').hide();
        var errorbox = $('#error').hide();
        if (data.error.code) {
            errorbox.find('.code').text(data.error.code);
        }
        if (data.error.friendly_message) {
            errorbox.find('.message').text(data.error.friendly_message);
        }
        errorbox.show();
    }

    function getExperiment() {
        oh.api.user.experiment.get({query: {id: def_expid}}, function (data) {
            loadExperiment(data);
        });
    }

    function loadExperiment(data) {
        if (data.status == 2) {
            var dockers = []
            for (var i in data.remote_servers) {
                dockers.push({
                    purl: "",
                    imgUrl: data.remote_servers[i].name == 'cloud_eclipse' ? '/static/pic/idehub.png' : '/static/pic/dseries.png',
                    name: data.remote_servers[i].name,
                    surl: data.remote_servers[i].name == 'cloud_eclipse' ? data.remote_servers[i].url + window.location.origin : data.remote_servers[i].url + "&oh=" + $.cookie('token')
                })
                list.push(temp.format(dockers[i]));
            }
            heartbeat(def_expid);
        } else if (data.status == 1) {
            setTimeout(getExperiment, 60000);
        } else {
            showErrorMsg(data);
        }
    }

    function bindEvent() {
        var work_center = $('.center').on('mouseover', 'iframe', function (e) {
            $(this).focus();
        });
        var hnav = $('.hackathon-nav').on('click', 'a.vm-box', function (e) {
            hnav.find('.vm-box').removeClass('active')
            var a = $(this).addClass('active');
            var url = a.data('url');
            var token = a.data('token');
            var name = a.attr('id')
            var ifrem = work_center.find('#' + name);
            work_center.find('iframe').addClass('invisible');
            if (ifrem.length > 0) {
                ifrem.removeClass('invisible');
            } else {
                ifrem = $('<iframe>').attr({
                    src: url,
                    id: name,
                    width: '100%',
                    height: '100%',
                    frameborder: 'no',
                    marginwidth: '0',
                    scrolling: 'no'
                }).appendTo(work_center)
            }
        });

        var smallbtn = $('<div class="smallscreen"><a class="glyphicon glyphicon-resize-small" href="javascript:;" ></a></div>')
            .click(function (e) {
                e.preventDefault();
                $('iframe[class!="invisible"]').removeClass('work-full');
                smallbtn.hide();
            }).appendTo('body');

        var fullbtn = $('#workfull').click(function (e) {
            e.preventDefault();
            $('iframe[class!="invisible"]').addClass('work-full');
            $('.smallscreen').show();
        });
    }

    function heartbeat(id) {
        oh.api.user.experiment.put({
            body: {id: id}
        }, function (data) {
            if (data.error) {
                // todo 'heartbeat error'
            } else {
                window.setTimeout(heartbeat(id), 300000)
            }
        });
    }

    function init() {
        pageload();
        bindEvent();
    }

    function endCountdown() {
        var timerTmpe = '{day}天{hour}小时{minute}分钟{second}秒';

        function show_time() {
            var timing = {day: 0, hour: 0, minute: 0, second: 0, distance: 0};
            this.time_server += 1000
            timing.distance = this.time_end - this.time_server;
            if (timing.distance > 0) {
                timing.day = Math.floor(timing.distance / 86400000)
                timing.distance -= timing.day * 86400000;
                timing.hour = Math.floor(timing.distance / 3600000)
                timing.distance -= timing.hour * 3600000;
                timing.minute = Math.floor(timing.distance / 60000)
                timing.distance -= timing.minute * 60000;
                timing.second = Math.floor(timing.distance / 1000)
                if (timing.day == 0) {
                    timing.day = null
                }
                if (timing.hour == 0 && timing.day == null) {
                    timing.hour = null
                }
                if (timing.minute == 0 && timing.hour == null) {
                    timing.minute = null
                }
                if (timing.second == 0 && timing.minute == null) {
                    timing.second = null
                }
                return timing;
            } else {
                return null;
            }
        }

        function showCountDown(countDown) {
            var timing = show_time.apply(countDown);
            if (!timing) {
                $('#timer').text('本次活动已结束，非常感谢您的参与。')
                clearInterval(stop);
            } else {
                $('#end_timer').text(timerTmpe.format(timing))
            }
        }

        var countDown = {
            time_server: new Date().getTime(),
            time_end: $('#end_timer').data('endtiem')
        }
        showCountDown(countDown);
        var stop = setInterval(function () {
            showCountDown(countDown);
        }, 1000);
    }

    $(function () {
        init();
        endCountdown();
    })
})(window.jQuery, window.oh);