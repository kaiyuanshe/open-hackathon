
        $(function(){
          $('input').iCheck({
            checkboxClass: 'icheckbox_square-blue',
            radioClass: 'iradio_square-blue',
            increaseArea: '20%' // optional
          });
          $("#rightSide").height($("body").height());

          $(".left .top div h3").each(function (i) {
            $(this).click(function () {
                /*if($("#hackathon-div").css("display")=="block"){
                            $(this).siblings().slideUp("slow");
                            $(".center .bottom").children().children().attr("height","500px");
                        }
                        else{
                            $(this).siblings().slideDown("slow");
                            $(".center .bottom").children().children().attr("height","380px");
                        }*/
                $(this).attr('class', 'clickOn');
                $(this).siblings().attr("class", "");
                $("#" + $(this).attr("name")).css("display", "block")
                $("#" + $(this).attr("name")).siblings().css("display", "none")
            });
          })
        });

