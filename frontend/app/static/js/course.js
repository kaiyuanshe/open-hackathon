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
                        var guaca = new String();
                        //alert(i.toString());
                        if (parseInt((i-1) / 3) == 0)
                                guaca = "http://osslab.cloudapp.net:28080/guacamole-0.9.2/client.xhtml?id=c%2Fubuntu";
                        if (parseInt((i-1) / 3) == 1)
                                guaca = "http://osslab.cloudapp.net:28080/guacamole-0.9.2/client.xhtml?id=c%2Fubuntu";
                        if (parseInt((i-1) / 3) == 2)
                                guaca = "http://osslab.chinacloudapp.cn:6080/guacamole-0.9.2/client.xhtml?id=c%2Fwindows";
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
                                word = "http://www.bing.com/search?q=python%20tutorial&qs=n&form=QBRE&pq=python%20tutorial&sc=0-0&sp=-1&sk=&cvid=6caade1422654b22a91072bdb5405d1ci&market=en-us";
                        if (i == 2)
                                word = "http://www.bing.com/search?q=ruby+tutorial&go=Submit&qs=n&form=QBRE&pq=ruby+tutorial&sc=0-0&sp=-1&sk=&cvid=f63da151989c4d788002d398b8e8911d&market=en-us";
                        if (i == 3)
                                word = "http://www.bing.com/search?q=node.js%20tutorial&qs=n&form=QBRE&pq=node.js%20tutorial&sc=4-14&sp=-1&sk=&cvid=aed6c35ebf4d415fa764a10580ebcb38&market=en-us";
                        if (i == 4)
                                word = "http://www.bing.com/search?q=mysql%20tutorial&qs=n&form=QBRE&pq=mysql%20tutorial&sc=8-10&sp=-1&sk=&cvid=3ebc1fb3db3d4ffeb7c7ee9a5d89ae0d&market=en-us";
                        if (i == 5)
                                word = "http://www.bing.com/search?q=mongodb%20tutorial&qs=n&form=QBRE&pq=mongodb%20tutorial&sc=8-15&sp=-1&sk=&cvid=ffdd9189a7814ff0924d7f033ce89a46&market=en-us";
                        if (i == 6)
                                word = "http://www.bing.com/search?q=redis%20tutorial&qs=n&form=QBRE&pq=redis%20tutorial&sc=2-14&sp=-1&sk=&cvid=ec63ccfc51b8402299aecf08911a247c&market=en-us";
                        if (i == 7)
                                word = "http://www.bing.com/search?q=.NET%20tutorial&qs=n&form=QBRE&pq=.net%20tutorial&sc=8-10&sp=-1&sk=&cvid=a319ade180de447d9c823d4dba457dc5&market=en-us";
                        if (i == 8)
                                word = "http://www.bing.com/search?q=typescript%20tutorial&qs=n&form=QBRE&pq=typescript%20tutorial&sc=2-19&sp=-1&sk=&cvid=1a85d80553334ae6b53d528b948d08ff&market=en-us";
                        if (i == 9)
                                word = "http://www.bing.com/search?q=Azure%20tutorial&qs=n&form=QBRE&pq=azure%20tutorial&sc=8-10&sp=-1&sk=&cvid=f42b51fec72140638217cd06550a9e9a&market=en-us";


                        //alert(word);
                        $("#vm").attr("src",guaca);
                        $("#document").attr("src",word);
}
});
