
        $(function(){            
            $(".center ul li").each(function(i){
                $(this).click(function(){
                    $(this).children().attr('class','selected');
                    $(this).siblings().children().attr("class","");
                    $("#"+$(this).attr("name")).css("display","block")
                    $("#"+$(this).attr("name")).siblings().css("display","none")
                })
            })
            
            $(".center .top div h3").each(function(i){
                $(this).click(function(){
                    /*if($("#hackathon-div").css("display")=="block"){
                        $(this).siblings().slideUp("slow");
                        $(".center .bottom").children().children().attr("height","500px");
                    }
                    else{
                        $(this).siblings().slideDown("slow");
                        $(".center .bottom").children().children().attr("height","380px");
                    }*/
                    $(this).attr('class','clickOn');
                    $(this).siblings().attr("class","");
                    $("#"+$(this).attr("name")).css("display","block")
                    $("#"+$(this).attr("name")).siblings().css("display","none")
                });
            })
        })


        function setFocusThickboxIframe() {
            document.getElementById("course_vm").contentWindow.focus();
            // alert("ok");
        }
        
        var clearAttrib=function(){
              var oSubWin=window.frames[1];
              if(oSubWin&&oSubWin.top&&oSubWin.parent){
                   oSubWin.parent=null;
                   oSubWin.top=null;
                   window.clearInterval(scanWin);
              }     
        }

       // var scanWin=window.setTimeout(clearAttrib,1);