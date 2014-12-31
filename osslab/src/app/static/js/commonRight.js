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

    $.ajax({
        url: '/api/registerlist',
        type: "GET",
        success: function (resp) {
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
        error: function () {
        }
    });
})

