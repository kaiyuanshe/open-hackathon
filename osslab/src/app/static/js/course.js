$(document).ready(function(){
    var course = getParameterByName("cid");
    $.ajax({
        url: '/api/course/' + course,
        type: "POST",
        success: function(resp){
//            var data = $.parseJSON(resp);
            var data=resp
            var servers = data.guacamole_servers;
            var show_url = data.output[0];


            if(servers.length > 0){
                $("#vm").attr("src",show_url);

                // refresh show site
                window.ivm = setInterval(function(){
                    $("#vm").attr("src", $("#vm").attr("src"));
                }, 3000);

                // heart beat
                window.ihb = setInterval(function(){
                    $.ajax({
                        url: '/api/course/' + data.course_id,
                        type: "PUT",
                        success: function(){},
                        error:function(){}
                    });
                }, 5000);

                $("#third-leave").click(function(){
                    $.ajax({
                        url: '/api/course/' + data.course_id,
                        type: "DELETE",
                        success: function(){
                            $("#vm").attr("src", "about:blank")
                            $("#course_vm").attr("src", "about:blank")
                            $("#servers").empty()
                            window.clearInterval(window.ivm);
                            window.clearInterval(window.ihb);
                        },
                        error:function(){
                            $("#vm").attr("src", "about:blank")
                            $("#course_vm").attr("src", "about:blank")
                        }
                    });
                });

                $("#servers").empty();
                $.each(servers, function(i,s){
                    var link = $("<a class='server-name'>"+s.name+"</a>").attr("title", s.name).click(function(){
                       $("#course_vm").attr("src",s.url);
                    });
                    $("#servers").append(link);
                });

                var sciv=setInterval(function(){
                    $.ajax({
                        url: '/api/course/' + data.course_id,
                        type: "GET",
                        success: function(data){
                            if(data.guacamole_status){
                                $("#course_vm").attr("src",servers[0].url);
                                clearInterval(sciv)
                            }
                            
                        },
                        error: function(){}
                    });
                },2000);
            }
        },
        error: function(){
            alert("course doesn't exist")
        }
    });
})
