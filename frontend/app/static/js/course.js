$(document).ready(function() {
var para = "type"
var url = window.location.href;
//:alert(url);
var theRequest = new Object();
	if (url.indexOf("?")!=-1) {
        	        var str  = url.substr(url.indexOf("?")+1);
                        var strs = str.split("&");
                        for (var i = 0;i < strs.length; i ++) {
                                theRequest[strs[i].split("=")[0]] = unescape(strs[i].split("=")[1]);
                        }
                        var i = parseInt(theRequest[para]);
                        /*var guaca = new String();
                        //alert(i.toString());
                        if (parseInt((i-1) / 3) == 0)
                                guaca = "http://osslab.cloudapp.net:28080/guacamole-0.9.2/client.xhtml?id=c%2Fubuntu";
                        if (parseInt((i-1) / 3) == 1)
                                guaca = "http://osslab.cloudapp.net:28080/guacamole-0.9.2/client.xhtml?id=c%2Fubuntu";
                        if (parseInt((i-1) / 3) == 2)
                                guaca = "http://osslab.chinacloudapp.cn:6080/guacamole-0.9.2/client.xhtml?id=c%2Fwindows";*/
                        var word = new String();
                        /*if (i == 1)
                                word = "http://en.wikipedia.org/wiki/Python_(programming_language)";
                        if (i == 2)
                                word = "http://en.wikipedia.org/wiki/Ruby_(programming_language)";
                        if (i == 3)
                                word = "http://en.wikipedia.org/wiki/JavaScript";
                        if (i == 4)
                                word = "http://www.mysql.com";
                        if (i == 5)
                                word = "http://www.mongodb.org";
                        if (i == 6)
                                word = "http://www.postgresql.org";
                        if (i == 7)
                                word = "http://www.microsoft.com/net";
                        if (i == 8)
                                word = "http://www.typescriptlang.org";
                        if (i == 9)
                                word = "http://azure.microsoft.com/en-us";
                        */
                        if (i == 1)
                                word = "http://www.bing.com/search?q=python%E5%9C%A8%E7%BA%BF%E6%95%99%E7%A8%8B&market=zh-cn";
                        if (i == 2)
                                word = "http://www.bing.com/search?q=ruby%E5%9C%A8%E7%BA%BF%E6%95%99%E7%A8%8B&market=zh-cn";
                        if (i == 3)
                                word = "http://www.bing.com/search?q=nodejs%E5%9C%A8%E7%BA%BF%E6%95%99%E7%A8%8B&market=zh-cn";
                        if (i == 4)
                                word = "http://www.bing.com/search?q=perl%E5%9C%A8%E7%BA%BF%E6%95%99%E7%A8%8B&market=zh-cn";
                        if (i == 5)
                                word = "http://www.bing.com/search?q=mysql%E5%9C%A8%E7%BA%BF%E6%95%99%E7%A8%8B&market=zh-cn";
                        if (i == 6)
                                word = "http://www.bing.com/search?q=mongodb%E5%9C%A8%E7%BA%BF%E6%95%99%E7%A8%8B&market=zh-cn";
                        if (i == 7)
                                word = "http://www.bing.com/search?q=redis%E5%9C%A8%E7%BA%BF%E6%95%99%E7%A8%8B&market=zh-cn";
                        if (i == 8)
                                word = "http://www.bing.com/search?q=typescript%E5%9C%A8%E7%BA%BF%E6%95%99%E7%A8%8B&market=zh-cn";
                        if (i == 9)
                                word = "http://www.bing.com/search?q=Azure%20tutorial&qs=n&form=QBRE&pq=azure%20tutorial&sc=8-10&sp=-1&sk=&cvid=f42b51fec72140638217cd06550a9e9a&market=en-us";


                        //alert(word);
                        //$("#vm").attr("src",guaca);
                        $("#document").attr("src",word);
}
});
