// google oauth
$(function() {
	$('#googlelogin').click(function() {
		login();
	});

	var clientId = "client_id=304944766846-7jt8jbm39f1sj4kf4gtsqspsvtogdmem.apps.googleusercontent.com";
	var redirect_uri = "redirect_uri=http://osslab.chinacloudapp.cn:5080/google";
	var scope = "scope=https://www.googleapis.com/auth/userinfo.profile+https://www.googleapis.com/auth/userinfo.email";
	var response_type = "response_type=token";
	
	function login() {
		var arr = [clientId,redirect_uri,scope,response_type];
		var url = "https://accounts.google.com/o/oauth2/auth?" + arr.join("&");
		location.href = url;
	}
});
