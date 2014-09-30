// google oauth
$(function() {
	$('#qqlogin').click(function() {
		login();
	});

	var clientId = "client_id=101157515";
	var redirect_uri = "redirect_uri=http://osslab.chinacloudapp.cn/qq";
	var scope = "scope=get_user_info";
	var state="state=osslab";
	var response_type = "response_type=code"
	
	function login() {
		var arr = [clientId,redirect_uri,scope,state,response_type];
		var url = "https://graph.qq.com/oauth2.0/authorize?" + arr.join("&");
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
