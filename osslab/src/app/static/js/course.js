$(document).ready(function(){
    var course = getParameterByName("cid");
    $.ajax({
        url: '/api/course/' + course,
        type: "POST",
        success: function(resp){
//            alert(resp);
            var data = $.parseJSON(resp);
            var servers = data.guacamole_servers;
            var show_url = data.output[0];

            if(servers.length > 0){
                $("#vm").attr("src",show_url);

                // refresh show site
                setInterval(function(){
                    $("#vm").attr("src", $("#vm").attr("src"));
                }, 3000);

                // heart beat
                setInterval(function(){
                    $.ajax({
                        url: '/api/course/' + data.course_id,
                        type: "PUT",
                        success: function(){}
                        error:function(){}
                    });
                }, 5000);

                $("#servers").empty();
                $.each(servers, function(i,s){
                    var link = $("<a class='server-name'>"+s.name+"</a>").attr("title", s.name).click(function(){
                       $("#course_if").attr("src",s.url);
                    });
                    $("#servers").append(link);
                })
                $("#course_if").attr("src",servers[0].url);
            }
        },
        error: function(){
            alert("course doesn't exist")
        }
    });
})
