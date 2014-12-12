$(document).ready(function () {
    var course = getParameterByName("cid");
    if(!course)
        course = "python"
    var main = $("#hack_main").on('mouseover','iframe',function(e){
        $(this).focus();
    });

    $.ajax({
        url: '/api/course/' + course,
        type: "POST",
        success: function (resp) {
            var data = resp
            var servers = data.guacamole_servers;

            if (servers.length > 0) {
                ul = $("<ul/>")
                // tips tab
                ul.append($('<li name="hack_main_tips"><div class="selected">Endpoints</div></li>'))

                // bar and iframe
                $.each(servers, function(i, s){
                    li = $('<li name="hack_main_'+s.name+'"></li>')
                    div = $('<div>'+s.name+'</div>')
                    div.data("data", s)
                    li.append(div)
                    ul.append(li)
                    sd = $('<div/>').attr("id", "hack_main_"+s.name)
                    var iframe = $('<iframe>').attr({
                        src:s.url,
                        width:'100%',
                        height:'600px',
                        frameborder:'yes',
                        marginwidth:'10',
                        scrolling:'yes'
                    }).appendTo(sd);
                    main.append(sd)
                })
                $("#hackathon_nav").append(ul)

                // show tips by default
                $("#hack_main_tips").show()
                $("#hack_main_tips").siblings().hide()

                // submit
                $("#submit").click(function () {
                    document.location.href = "/submitted";
                })

                // public urls
                if (data.public_urls.length > 0){
                    $.each(data.public_urls, function(i,u){
                        var web_link = $("<a/>").attr({
                            target: "_blank",
                            href: u.url,
                            style: "margin-top:20px"
                        }).html(u.url).appendTo($("#hack_pub_web"))
                    })
                }

                // nav bar events
                $(".center .mid ul li").each(function (i) {
                    $(this).click(function () {
                        $(this).children().attr('class', 'selected');
                        $(this).siblings().children().attr("class", "");
                        $("#" + $(this).attr("name")).show()
                        $("#" + $(this).attr("name")).siblings().hide()
                    })
                })

                // heart beat
                var ihb = setInterval(function () {
                    $.ajax({
                        url: '/api/course/' + data.expr_id,
                        type: "PUT",
                        success: function () {},
                        error: function () {}
                    });
                }, 1000*60*2);

                // cancel button click event
                $("#third-leave").click(function () {
                    if(confirm("所有环境将被取消，请确保你的更改已提交至github。您确定取消么？")){
                        $.ajax({
                            url: '/api/course/' + data.expr_id,
                            type: "DELETE",
                            success: function () {
                                $("#hack_main_cancelled").show()
                                $("#hack_main_cancelled").siblings().hide()
                                clearInterval(ihb);
                                setInterval(function(){
                                    document.location.href = "/settings"
                                }, 5000);
                            },
                            error: function () {
                                clearInterval(ihb);
                                alert(error)
                            }
                        });
                    }
                    return false;
                });

                $("#new-window").click(function(){
                    data = $(".center .mid ul li .selected").data("data")
                    if(data && data.url){
                        detach_url= "redirect?url=" + encodeURIComponent(data.url);
                        $("#new-window").attr("href",detach_url);
                        return true;
                    }else{
                        $("#new-window").attr("href", "#");
                        return false;
                    }
                });

                var sciv = setInterval(function () {
                    $.ajax({
                        url: '/api/course/' + data.expr_id,
                        type: "GET",
                        success: function (data) {
                            if (data.guacamole_status) {
                                clearInterval(sciv)

                                detach_url= "redirect?url=" + encodeURIComponent(servers[0].url);
                                $("#new-window").attr("href",detach_url);
                            }
                        },
                        error: function () {
                            clearInterval(sciv)
                        }
                    });
                }, 2000);
            }
        },
        error: function () {
            $("#hack_main_error").show();
            $("#hack_main_error").siblings().hide();
        }
    });

    $(".center .top div h3").each(function (i) {
        $(this).click(function () {
            /*if($("#hackathon-div").css("display")=="block"){
                        $(this).siblings().slideUp("slow");
                        $(".center .bottom").children().children().attr("height","500px");
                    }
                    else{
                        $(this).siblings().slideDown("slow");
                        $(".center .bottom").children().children().attr("height","380px");
                    }*/
            $(this).attr('class', 'clickOn');
            $(this).siblings().attr("class", "");
            $("#" + $(this).attr("name")).css("display", "block")
            $("#" + $(this).attr("name")).siblings().css("display", "none")
        });
    })

})

