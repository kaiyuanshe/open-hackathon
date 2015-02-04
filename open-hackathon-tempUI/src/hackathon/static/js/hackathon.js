$(document).ready(function() {

    var ifrem = $();

    var cid = getParameterByName("cid");
    if (!cid || typeof(cid) == "undefined")
        cid = "ut"
    var main = $("#hack_main").on('mouseover', 'iframe', function(e) {
        $(this).focus();
    });
    var $timer = $('#end_timer');
    var timerTmpe = '{day}天{hour}小时{minute}分钟{second}秒'
    Countdown(endDate, function(timer) {
        if (timer) {
            $timer.text(timerTmpe.format(timer))
        } else {
            $('#timer').text('本次活动已结束，非常感谢您的参与。')
        }
    })
    api_stat(function(data) {
        var str = '  <h4 class="text-center">在线人数：<span>{online} </span> 参赛人数：<span>{total}</span></h4>';
        $('#stat').html(str.format(data));
    })
    $('.nav a[data-action="fullscreen"]').bind('click', function(e) {
        $('.center iframe[class!="invisible"]').addClass('work-full')
    });
    $(document, 'html,body,iframe').keydown(function(e) {
        e = window.event || e || e.which;
        if (e.ctrlKey && e.which == 113) {
            ifrem.toggleClass('work-full');
            e.preventDefault()
            return false;
        }
    });

    function checkstart(id, callback) {
        setTimeout(loopstart);

        function loopstart() {
            hget('/api/user/experiment?id=' + id,
                function(data) {
                    if (data.guacamole_servers.length > 0) {
                        callback(data)
                    } else {
                        setTimeout(loopstart, 60000);
                    }
                },
                function(err) {
                    callback(err);
                }
            );
        };
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
                            <h4>{name}<h4>\
                        </div>\
                    </div>';
            checkstart(data.expr_id, function(data) {
                var servers = data.guacamole_servers;
                var work_center = $('.center');
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
                            frameborder: 'yes',
                            marginwidth: '10',
                            scrolling: 'yes'
                        }).appendTo(work_center)
                    }
                });
                $.each(servers, function(i, s) {
                    hnav.append(tmpe.format(s));
                });
                hnav.find('a.vm-box:eq(0)').trigger('click');
            })
        },
        function() {

        }
    );
})

