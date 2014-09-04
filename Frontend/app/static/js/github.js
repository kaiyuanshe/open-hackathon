// google oauth
$(function() {
	$('#githublogin').click(function() {
		login();
	});

	var clientId = "client_id=0eded406cf0b3f83b181";
	var redirect_uri = "redirect_uri=http://osslab.chinacloudapp.cn:5080/github";
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
