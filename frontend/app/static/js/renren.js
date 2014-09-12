//renren oauth	
$(function() {
        $('#renrenlogin').click(function() {
                login();
        });

        var clientId = "client_id=7e0932f4c5b34176b0ca1881f5e88562";
        var redirect_uri = "redirect_uri=http://osslab.chinacloudapp.cn:5080/renren";
        var scope = "scope=read_user_message+read_user_feed+read_user_photo";
        var response_type = "response_type=token";
	var display = "display=page";
//	var state = clientID;

        function login() {
                var arr = [clientId,redirect_uri,response_type,display];
                var url = "https://graph.renren.com/oauth/authorize?" + arr.join("&");
                location.href = url;
        }
});

