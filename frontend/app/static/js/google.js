// google oauth
$(function() {
	$('#googlelogin').click(function() {
		login();
	});

	var clientId = "client_id=304944766846-7jt8jbm39f1sj4kf4gtsqspsvtogdmem.apps.googleusercontent.com";
	var localurl = location.href;
	var redirect_uri = "redirect_uri=" + localurl + "google";
	var scope = "scope=https://www.googleapis.com/auth/userinfo.profile+https://www.googleapis.com/auth/userinfo.email";
	var response_type = "response_type=token";
	
	function login() {
		var arr = [clientId,redirect_uri,scope,response_type];
		var url = "https://accounts.google.com/o/oauth2/auth?" + arr.join("&");
		location.href = url;
	}
});
 $(function() {
                        $(document).ready(function() {
                                Display();
                        });

                        function getUrlparam(name) {
                                var reg = new RegExp("(^|&)"+ name +"=([^&]*)(&|$)");
                                var r = window.location.search.substr(1).match(reg);
                                if (r!=null) return unescape(r[2]); return null;
                        }

                        function Display() {
                                var name = "access_token";
                                var url = window.location.href;
                                var theRequest = new Object();
                                if (url.indexOf("#")!=-1) {
                                        var str = url.substr(url.indexOf("#")+1);
                                        var strs = str.split("&");
                                        for (var i = 0;i < strs.length;i ++)
                                        {
                                        theRequest[strs[i].split("=")[0]] = unescape(strs[i].split("=")[1]);
                                        }
                                        newurl = "https://www.googleapis.com/oauth2/v1/userinfo?access_token=" + theRequest[name];
                                        $.ajax({
                                                type : "GET",
                                                url : newurl,
                                                dataType : "jsonp",
                                                success: function(msg) {
                                                         $("#name").html('<p style = "color:white">' + msg.name  + "</p>");
                                                         $("#photo").html('<img src = "' + msg.picture + '" height = "30" width = "30"/>');
							 document.cookie = 'username=' + msg.name;
							 document.cookie = 'picurl=' + msg.picture;
							 var pre = window.location.host;
                                                         for (var i = 1;i <= 9;i++) {
                                                                name = "#image" + i.toString();
                                                                url = "course?type=" + i.toString();
                                                                $(name).attr("href",url);
                                                         }
                                                },
                                                error : function(msg) {
                                                        alert("something is wrong!\n" + msg.d);
                                                }
                                        });
                                }
                        }
                });

