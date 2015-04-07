// -----------------------------------------------------------------------------------
// Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
//  
// The MIT License (MIT)
//  
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//  
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//  
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.
// -----------------------------------------------------------------------------------

// need refactor
//renren oauth
$(function() {
        $('#renrenlogin').click(function() {
                login();
        });

        var clientId = CONFIG.renren.clientID;
        var redirect_uri = CONFIG.renren.redirect_url;
        var scope = CONFIG.renren.scope;
        var response_type = CONFIG.renren.response_type;
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
                                        var tmpurl = "http://hackathon.chinacloudapp.cn:5080/renren";
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


