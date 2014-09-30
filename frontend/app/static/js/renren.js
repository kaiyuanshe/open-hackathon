//renren oauth	
$(function() {
        $('#renrenlogin').click(function() {
                login();
        });

        var clientId = "client_id=7e0932f4c5b34176b0ca1881f5e88562";
        var redirect_uri = "redirect_uri=http://osslab.chinacloudapp.cn/renren";
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
                                //var urls = url.split('#');
                                //location.href = urls.join(l?');
                                var theRequest = new Object();
                                if (url.indexOf("#")!=-1) {
                                        var urls = url.split('#');
                                        location.href = urls.join('?');

                                        var str = url.substr(url.indexOf("#")+1);
                                        var strs = str.split("&");
                                        for (var i = 0;i < strs.length;i ++)
                                        {
                                        theRequest[strs[i].split("=")[0]] = unescape(strs[i].split("=")[1]);
                                        }
                                        newurl_h = "https://api.renren.com";
                                        newurl_t = "m/v2/user/get?access_token=" +  theRequest[name];
                                        newurl = "https://api.renren.com/v2/user/get?access_token=" +  theRequest[name] /*+ "&state=7e0932f4c5b34176b0ca1881f5e88562" + "&jsoncallback=?"*/;
        //                              $("#content").html("<p>" + newurl +" " +  theRequest[name]  + "</p>");
                                        var tmpurl = "http://osslab.chinacloudapp.cn:5080/renren";
        //                              location.href = newurl;
                                        /*$.ajax({
                                                type : "GET",
                                                url : newurl,
                                                datatype : "jsonp" ,
                                                success: function(msg) {
                                                        alert("ok");
                                                },
                                                error : function(msg) {
                                                        alert("something is wrong!\n" + msg.d);
                                                }
                                        });*/
                                        //$("#content").html("<p>" + name + " " + "</p>");
                                }
                        }
                });

