$(document).ready(function() {

    var ifrem = $();
     setTimeout(function(){
        $('#tooltip').fadeOut(2000);
     }, 1500);
    var cid = getParameterByName("cid");
    if (!cid || typeof(cid) == "undefined")
        cid = "ut"
    var main = $("#hack_main").on('mouseover', 'iframe', function(e) {
        $(this).focus();
    });
    api_stat(function(data) {
        var str = '  <h4 class="col-md-offset-1">在线人数：<span>{online} </span></h4><h4  class="col-md-offset-1">参赛人数：<span>{total}</span></h4>';
        $('#stat').html(str.format(data));
    })
    $(document).bind('tiemer', function(e, d) {
        var $timer = $('#end_timer');
        var timerTmpe = '{day}天{hour}小时{minute}分钟{second}秒';
        if (d.end_time) {
            var enddate = new Date(Date.parse(d.end_time.replace(/-/g, '/')))
            Countdown(enddate, function(timer) {
                if (timer) {
                    $timer.text(timerTmpe.format(timer))
                } else {
                    $('#timer').text('本次活动已结束，非常感谢您的参与。')
                }
            })
        } else {
            $('#timer').text('本次活动已结束，非常感谢您的参与。')
        }
    });
    var smscress = $('.smallscreen').on('click', 'a', function(e) {
        ifrem.removeClass('work-full');
        smscress.hide();
    })
    $('.nav a[data-action="fullscreen"]').bind('click', function(e) {
        ifrem.addClass('work-full')
        smscress.show();
    });
    /*$(document, 'html,body,iframe').keydown(function(e) {
        e = window.event || e || e.which;
        if (e.ctrlKey && e.which == 113) {
            ifrem.toggleClass('work-full', function(e) {
                console.log();
            });
            e.preventDefault()
            return false;
        }
    });*/

    function checkstart(id, callback) {
        setTimeout(loopstart);

        function loopstart() {
            hget('/api/user/experiment?id=' + id,
                function(data) {
                    if (data.status == 2) { // expr is running
                        callback(data)
                    } else if (data.status == 1) { // expr is starting
                        setTimeout(loopstart, 60000);
                    } else {
                       showErrorMsg()
                    }
                },
                function(err) {
                    callback(err);
                }
            );
        };
    }

    function showErrorMsg(code,msg){
        $('#load').hide();
        var errorbox =  $('#error');
        if(code){
            errorbox.find('.code').text(code);
        }
        if(msg){
            errorbox.find('.message').text(msg);
        }
        errorbox.show();
    }

    hpost('/api/user/experiment', {
            "cid": cid,
            "hackathon": CONFIG.hackathon.name
        },
        function(resp) {
            var data = resp
            var tmpe = '<div class="row ">\
                        <div class="col-md-12 text-center">\
                            <a href="javascript:;" title="" class="vm-box"  id="{name}"  data-url="{url}">\
                                <img src="/static/pic/dseries.png" alt="">\
                            </a>\
                            <h4 name="dserie">{name}<h4>\
                        </div>\
                    </div>';
            checkstart(data.expr_id, function(data) {
                var servers = data.remote_servers || data.guacamole_servers;
                var work_center = $('.center').on('mouseover', 'iframe', function(e) {
                    $(this).focus();
                });
                var hnav = $(".hackathon-nav").on('click', 'a.vm-box', function(e) {
                    hnav.find('.vm-box').removeClass('active')
                    var a = $(this).addClass('active');
                    var url = a.data('url');
                    var name = a.attr('id')
                    ifrem = work_center.find('#' + name);
                    work_center.find('iframe').addClass('invisible');
                    if (ifrem.length > 0) {
                        ifrem.removeClass('invisible');
                    } else {
                        ifrem = $('<iframe>').attr({
                            src: url + "&token=" + get_token(),
                            id: name,
                            width: '100%',
                            height: '100%',
                            frameborder: 'no',
                            marginwidth: '0',
                            scrolling: 'no',
                        }).appendTo(work_center)
                    }
                });

                $.each(servers, function(i, s) {
                    var puburls = s.public_urls || data.public_urls
                    var vm = $(tmpe.format(s))
                    $.each(puburls, function(i, urls) {
                        vm.find('h4[name]').append('<h4 class="col-md-offset-1">您在开发环境部署的应用或网站可访问下面地址：</h4><h4 class="col-md-offset-1"><a href="{url}" target="_blank">{url}</a></h4>'.format(urls))
                    });
                    hnav.append(vm);
                });
                hnav.find('a.vm-box:eq(0)').trigger('click');
            })
        },
        function(data) {
            $('#load').hide();
            $('#error').show();
        }
    );
})
