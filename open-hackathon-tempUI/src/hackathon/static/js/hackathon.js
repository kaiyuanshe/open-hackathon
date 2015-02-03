$(document).ready(function () {
    var cid = getParameterByName("cid");
    if(!cid || typeof(cid)=="undefined")
        cid = "ubuntu"
    var main = $("#hack_main").on('mouseover','iframe',function(e){
        $(this).focus();
    });

    var hackathon = CONFIG.hackathon.name

    hpost('/api/user/experiment',{
            "cid": cid,
            "hackathon": hackathon
        },
        function (resp) {
            var data = resp
            var servers = data.guacamole_servers;
            if (servers.length > 0) {
                var  ul = $("<ul>");
                // tips tab
                // ul.append($('<li name="hack_main_tips"><div class="selected">Endpoints</div></li>'))
                // bar and iframe
                $.each(servers, function(i, s){
                    if (s.name=="Deploy") {
                        var li = $('<li name="hack_main_'+s.name+'"></li>');
                        li.append($('<div>').data("data", s).text(s.name)).appendTo(ul);
                        var sd = $('<div>').attr({"id":"hack_main_"+s.name}).addClass("selected")
                        main.append(sd);
                        var iframe = $('<iframe>').attr({
                            src:s.url+"&token=" + get_token(),
                            width:'100%',
                            height:'600px',
                            frameborder:'yes',
                            marginwidth:'10',
                            scrolling:'yes'
                        }).appendTo(sd);
                    }
                })
                $("#hackathon_nav").append(ul)

                // show tips by default
                $("#hack_main_tips").removeClass('hidden');
                $("#hack_main_tips").siblings().addClass('hidden');

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
                $(".center .mid ul li").click(function () {
                    var li = $(this);
                    var name = '#'+li.attr("name");
                    var url = li.data().iframe;
                    li.children().addClass('selected');
                    li.siblings().children().removeClass("selected")
                    $(name).removeClass('hidden').siblings().addClass('hidden');
                })


                // heart beat
                var ihb = setInterval(function () {
                    hput('/api/user/experiment',{
                            "id": data.expr_id
                        },
                        function () {},
                        function () {}
                    );
                }, 1000*60*2);

                // cancel button click event
                $("#third-leave").click(function () {
                    if(confirm("所有环境将被取消，请确保你的更改已提交至github。您确定取消么？")){
                        hdelete('/api/user/experiment?id=' + data.expr_id,
                            function () {
                                $("#hack_main_cancelled").show()
                                $("#hack_main_cancelled").siblings().hide()
                                clearInterval(ihb);
                                setInterval(function(){
                                    document.location.href = "/settings"
                                }, 5000);
                            },
                            function () {
                                clearInterval(ihb);
                                alert(error)
                            }
                        );
                    }
                    return false;
                });

                $("#new-window").click(function(){
                    data = $(".center .mid ul li .selected").data("data")
                    if(data && data.url){
                        detach_url= "redirect?url=" + encodeURIComponent(s.url+"&token=" + get_token());
                        $("#new-window").attr("href",detach_url);
                        return true;
                    }else{
                        $("#new-window").attr("href", "#");
                        return false;
                    }
                });

                var sciv = setInterval(function () {
                    hget('/api/user/experiment?id=' + data.expr_id,
                        function (data) {
                            if (data.guacamole_status) {
                                clearInterval(sciv)

                                detach_url= "redirect?url=" + encodeURIComponent(servers[0].url);
                                $("#new-window").attr("href",detach_url);
                            }
                        },
                        function () {
                            clearInterval(sciv)
                        }
                    );
                }, 1000 * 60);
            }
        },
        function () {
            $("#hack_main_error").show();
            $("#hack_main_error").siblings().hide();
        }
    );

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

