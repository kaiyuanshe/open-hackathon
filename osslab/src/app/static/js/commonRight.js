
        $(function(){
            daoJiShi();
            $("#logout p").click(function() {
                window.location.href="/logout";
            })
        })
        
        var endDate=new Date(2014,11,17,18,00,00);//年月日时分秒，月要减去1
        function daoJiShi()
        {
         var now=new Date();
         var oft=Math.round((endDate-now)/1000);
         var ofd=parseInt(oft/3600/24);
         var ofh=parseInt((oft%(3600*24))/3600);
         var ofm=parseInt((oft%3600)/60);
         var ofs=oft%60;
         document.getElementById('timer').innerHTML='<h4>还有 '+ofd+' 天 ' +ofh+ ' 小时 ' +ofm+ ' 分钟 ' +ofs+ ' 秒</h4>';
         if(ofs<0){document.getElementById('timer').innerHTML='倒计时结束！';return;};
         setTimeout('daoJiShi()',1000);
        };