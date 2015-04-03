// -----------------------------------------------------------------------------------
// Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
//  
// The MIT License (MIT)
//  
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//  
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//  
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.
// -----------------------------------------------------------------------------------

$(function() {


    $(document).bind('tiemer', function(e, d) {
        var $timer = $('#end_timer');
        var timerTmpe = '{day}天{hour}小时{minute}分钟{second}秒';
        if (d.end_time) {
            Countdown(d.end_time, function(timer) {
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
    api_stat(function(){})
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
