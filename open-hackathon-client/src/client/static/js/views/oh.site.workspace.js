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
        var temp_name = $.getUrlParam('t');
        def_expid = $('[data-experiment]').data('experiment') || 0;
        if (def_expid) {
            getExperiment(def_expid)
        } else {
            getTemplate(temp_name);
        }
        teamMember();
        hackathonStat();
    }

    function teamMember() {
//        oh.api.team.member.list.get({header: {hackathon_name: hackathon_name}}, function (data) {
//            // todo 'Response team member'
//            if (data.error) {
//
//            } else {
//
//            }
//            console.log(data);
//        });
    }

    function hackathonStat() {
        oh.api.hackathon.stat.get({
            header: {hackathon_name: hackathon_name}
        }, function (data) {
            $('#online').text(data.online);
            $('#total').text(data.register);
            //setTimeout(hackathonStat(), 600000)
        });
    }

    function getTemplate(name) {
        oh.api.hackathon.template.get({header: {hackathon_name: hackathon_name}}, function (data) {
            if (data.error) {
                showErrorMsg(data);
            } else {
                
                if (data.length > 0) {
                    def_expid = data[0].id;
                    var tname = data[0].name;
                    $.each(data,function(i,item){
                        if(item.name == name){
                            def_expid = item.id;
                            tname = item.name;
                        }
                    });
                    postTemplate(tname);
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
            body: {template_name: name, hackathon_name: hackathon_name}
        }, function (data) {
            loadExperiment(data);
        });
    }

    function showErrorMsg(data) {
        $('#load').hide();
        var errorbox = $('#error').hide();
        if(data.error) {
          if (data.error.code) {
              errorbox.find('.code').text(data.error.code);
          }
          if (data.error.friendly_message) {
              errorbox.find('.message').text(data.error.friendly_message);
          }
        } else {
          errorbox.find('.message').text('部署实验环境失败，这可能是模板错误造成的，请联系系统管理员');
        }
        errorbox.show();
    }

    function getExperiment(expr_id) {
        oh.api.user.experiment.get({query: {id: expr_id}}, function (data) {
            loadExperiment(data);
        });
    }

    function get_guacamole_server_name(id, type, datasource) {
        return btoa([
            id,
            type,
            datasource
        ].join('\0'));
    };

    function loadExperiment(data) {
        var tmpe = '<div class="row ">\
                        <div class="col-md-12 text-center">\
                            <a href="javascript:;" title="" class="vm-box"  id="{name}"  data-url="{surl}">\
                                <img src="{imgUrl}" alt="">\
                            </a>\
                            <h4 name="dserie">{name}<h4>\
                        </div>\
                    </div>';
        var url_tmpe = '<h4><a href="{url}" target="_blank" style="text-decoration:underline;color:#00abec;" class="col-md-offset-1">{name}</a></h4>';
        if (data.status == 2) {
            var dockers = []
            for (var i in data.remote_servers) {
                dockers.push({
                    purl: "",
                    imgUrl: '/static/pic/dseries.png',
                    name: data.remote_servers[i].name,
                    surl: data.remote_servers[i].guacamole_host + "/guacamole/#/client/" + get_guacamole_server_name(data.remote_servers[i].name, "c", "openhackathon") + "?oh=" + $.cookie('token') + "&name=" + data.remote_servers[i].name + "&_=" + new Date().getTime()
                    })
                $('#show').append(tmpe.format(dockers[i]));
            }
            if(data.public_urls.length>0){
                $('#show').append('<h4 class="col-md-offset-1">您可访问下面地址：</h4>');
            }
            $.each(data.public_urls,function(i,url){
                $('#show').append(url_tmpe.format(url));
            });
            
            $('.hackathon-nav a.vm-box:eq(0)').trigger('click');
            heartbeat(data.expr_id);
        } else if (data.status == 1) {
            setTimeout(function(){
                           getExperiment(data.expr_id)
                       }, 5000);
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
                window.setTimeout(function(){
                        heartbeat(id)
                    }, 300000)
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
