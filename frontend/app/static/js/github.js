// google oauth
$(function() {
	$('#githublogin').click(function() {
		login();
	});

	var clientId = "client_id=0eded406cf0b3f83b181";
	var redirect_uri = "redirect_uri=http://osslab.chinacloudapp.cn/github";
	var scope = "scope=user";
	
	function login() {
		var arr = [clientId,redirect_uri,scope];
		var url = "https://github.com/login/oauth/authorize?" + arr.join("&");
		location.href = url;
		/*$.ajax({
                    type : "GET",
                    url : url,
                    datatype : "jsonp",
                    success: function(msg) {
                                 alert(msg.name);
                             },
                    error : function(msg) {
                                 alert("something is wrong!\n" + msg.d);
                             }
                });*/
	}
});
/*
 $(document).ready(function() {
                function canvasvalue(id ,text) {
                        canvas = document.getElementById(id);
                        ctx = canvas.getContext('2d');
                        //ctx.fillStyle = color;
                        //ctx.fillRect(0,0,400,400);
                        ctx.font = "100px Times New Roman";
                        //ctx.textAlign = "left";
                        ctx.fillText(text,120-text.length*10,160);
                }
                canvasvalue('canvas1',"Python");
                canvasvalue('canvas2',"Ruby");
                canvasvalue('canvas3',"Perl");
                canvasvalue('canvas4',"Mysql");
                canvasvalue('canvas5',"Mongodb");
                canvasvalue('canvas6',"Redis");
                canvasvalue('canvas7',".NET");
                canvasvalue('canvas8',"Typescript");
                canvasvalue('canvas9',"Azure");

                 for (var i = 1;i <= 9;i++) {
                        name = "#image" + i.toString();
                        url = "http://osslab.chinacloudapp.cn:5080/course?type=" + i.toString();
                        $(name).attr("href",url);
                }

                });
*/
