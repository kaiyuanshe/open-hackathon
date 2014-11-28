$(document).ready(function () {
    var course = getParameterByName("cid");
    course = "jstorm"


    $.ajax({
        url: '/api/course/' + course,
        type: "POST",
        success: function (resp) {
            var data = resp
            var servers = data.guacamole_servers;

            // coding here in success() is specially for jStorm.
            $("#course_vm1").attr("src", "http://jstorm.sourceforge.net")
            $("#course_vm2").attr("src", "http://flask.pocoo.org/")

            if (servers.length > 0) {
                var show_url = data.output[0];
                $("#course_vm3").attr("src", show_url);

                $("#submit").removeAttr("disabled");
                $("#submit").click(function () {
                    document.location.href = "/submitted";
                })

                // refresh show tab
                //                window.ivm = setInterval(function(){
                //                    $("#course_vm3").attr("src", $("#course_vm3").attr("src"));
                //                }, 3000);

                // heart beat
                var ihb = setInterval(function () {
                    $.ajax({
                        url: '/api/course/' + data.course_id,
                        type: "PUT",
                        success: function () {},
                        error: function () {}
                    });
                }, 5000);

                $("#third-leave").click(function () {
                    $.ajax({
                        url: '/api/course/' + data.course_id,
                        type: "DELETE",
                        success: function () {
                            $("#course_vm3").attr("src", "about:blank")
                            $("#course_vm4").attr("src", "about:blank")
                            //                            window.clearInterval(window.ivm);
                            clearInterval(ihb);
                            $("#submit").attr("disabled", "disabled");
                        },
                        error: function () {
                            $("#course_vm3").attr("src", "about:blank")
                            $("#course_vm4").attr("src", "about:blank")
                            //                            window.clearInterval(window.ivm);
                            clearInterval(ihb);
                            $("#submit").attr("disabled", "disabled");
                        }
                    });
                    return false;
                });

                //                $.each(servers, function(i,s){
                //                    var link = $("<a class='server-name'>"+s.name+"</a>").attr("title", s.name).click(function(){
                //                       $("#course_vm").attr("src",s.url);
                //                       $(this).addClass("selected");
                //                       $(this).siblings().remove("selected");
                //                    });
                //                    if(i==0){
                //                        link="<a class='server-name selected' title='"+s.name+"'>"+s.name+"</a>";
                //                    }
                //                    $("#servers").append(link);
                //                });

                var sciv = setInterval(function () {
                    $.ajax({
                        url: '/api/course/' + data.course_id,
                        type: "GET",
                        success: function (data) {
                            if (data.guacamole_status) {
                                $("#course_vm4").attr("src", servers[0].url);
                                clearInterval(sciv)

                                $("#new-window").attr("href", servers[0].url);
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
            // alert("course doesn't exist")
            $("#course_vm1").attr("src", "/error")
            $("#course_vm2").attr("src", "/error")
            $("#course_vm3").attr("src", "/error")
            $("#course_vm4").attr("src", "/error")
        }
    });

    $(".center ul li").each(function (i) {
        $(this).click(function () {
            $(this).children().attr('class', 'selected');
            $(this).siblings().children().attr("class", "");
            $("#" + $(this).attr("name")).css("display", "block")
            $("#" + $(this).attr("name")).siblings().css("display", "none")
        })
    })

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

function setFocusThickboxIframe() {
    document.getElementById("course_vm").contentWindow.focus();
    // alert("ok");
}