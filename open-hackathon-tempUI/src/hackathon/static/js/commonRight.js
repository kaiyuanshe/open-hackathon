$(function() {


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
    api_stat()
    $("#logout").click(function() {
        window.location.href = "/logout";
    })

    hget('/api/register/list',
        function(resp) {
            // USER LIST
            var container = $("#userList ul")
            var online = 0
            $.each(resp, function(i, r) {
                register = $.parseJSON(r)
                var state = $("<div/>").addClass("circle");
                if (register.online == 1) {
                    state.addClass("online")
                    online = online + 1
                }
                var usr = $("<div/>").addClass("userName").html(register.register_name)
                $("<li/>").append(state).append(usr).appendTo(container);
            });

            // user statistics
            $("#registered_count").html("<h4>注册人数:" + resp.length + "</h4>")
            $("#online_count").html("<h4>在线人数:" + online + "</h4>")
        },
        function() {}
    );

    setInterval(function() {
        hget('/api/bulletin',
            function(resp) {
                anmt = $.parseJSON(resp)
                $("#anmt").text(anmt.content)
            },
            function() {}
        );
    }, 3 * 60 * 1000);

})
