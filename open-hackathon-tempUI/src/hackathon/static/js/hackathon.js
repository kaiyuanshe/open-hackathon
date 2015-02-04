$(document).ready(function() {
    var cid = getParameterByName("cid");
    if (!cid || typeof(cid) == "undefined")
        cid = "ubuntu"
    var main = $("#hack_main").on('mouseover', 'iframe', function(e) {
        $(this).focus();
    });
    var $timer = $('#end_timer');
    var timerTmpe = '{day}天{hour}小时{minute}分钟{second}秒'
    Countdown(endDate, function(timer) {
        if (timer) {
            $timer.text(timerTmpe.format(timer))
        } else {
            $('#timer').text('本次活动以结束，非常感谢您的参与。')
        }
    })
    var hackathon = CONFIG.hackathon.name

    function checkstart(id,callback) {
        setTimeout(loopstart);

        function loopstart() {
            hget('/api/user/experiment?id=' + id,
                function(data) {
                    if (data.guacamole_servers.length>0) {
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
            "hackathon": hackathon
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

            checkstart(data.expr_id,function(data) {
                var servers = data.guacamole_servers;
                var work_center = $('.center');
                var hnav = $(".hackathon-nav").on('click', 'a.vm-box', function(e) {
                    var a = $(this);
                    var url = a.data('url');
                    var name = a.attr('id')
                    var ifrem = work_center.find('#' + name);
                    work_center.find('iframe').css({
                        visibility: 'hidden'
                    });
                    if (ifrem.length > 0) {
                        ifrem.css({
                            visibility: 'visible'
                        });
                    } else {
                        work_center.append($('<iframe>').attr({
                            src: url + "&token=" + get_token(),
                            id: name,
                            width: '100%',
                            height: '100%',
                            frameborder: 'yes',
                            marginwidth: '10',
                            scrolling: 'yes'
                        }))
                    }
                });
                hnav.find('a.vm-box:eq(0)').trigger('click');
                $.each(servers, function(i, s) {
                    hnav.append(tmpe.format(s));
                })
            })

        },
        function() {

        }
    );
})
