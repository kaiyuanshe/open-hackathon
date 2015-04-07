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

$(function(){
    //daoJiShi();
    var endDate=new Date(2015,11,17,18,00,00);//年月日时分秒，月要减去1
    $('#timer').flipcountdown({size:"sm",
        tick:function(){
            var nol = function(h){
                return h>9?h:'0'+h;
            }
            var now=new Date();
            var oft=Math.round((endDate-now)/1000);
            var ofd=parseInt(oft/3600/24);
            var ofh=parseInt((oft%(3600*24))/3600);
            var ofm=parseInt((oft%3600)/60);
            var ofs=oft%60;
            return nol(ofd)+' '+nol(ofh)+' '+nol(ofm)+' '+nol(ofs);
        }
    });

    $("#logout p").click(function() {
        window.location.href="/logout";
    })

    hget('/api/registerlist',
        function (resp) {
            // USER LIST
            var container = $("#userList ul")
            var online=0
            $.each(resp, function(i, r){
                register = $.parseJSON(r)
                var state = $("<div/>").addClass("circle");
                if (register.online==1){
                    state.addClass("online")
                    online = online + 1
                }
                var usr = $("<div/>").addClass("userName").html(register.register_name)
                $("<li/>").append(state).append(usr).appendTo(container);
            });

            // user statistics
            $("#registered_count").html("<h4>注册人数:"+ resp.length +"</h4>")
            $("#online_count").html("<h4>在线人数:"+ online +"</h4>")
        },
        function () {
        }
    );

    setInterval(function(){
        hget('/api/announcement',
            function (resp) {
                anmt = $.parseJSON(resp)
                $("#anmt").text(anmt.content)
            },
            function () {
            }
        );
    }, 3*60*1000);

})

