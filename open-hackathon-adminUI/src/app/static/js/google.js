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

// google oauth
$(function() {
    $('#googlelogin').click(function() {
        login();
    });

    var clientId = CONFIG.google.clientID;
    var localurl = location.href;
    var redirect_uri = CONFIG.google.redirect_url;
    var scope = CONFIG.google.scope;
    var response_type = CONFIG.google.response_type;

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

