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

    $("#submit").click(function(){
        cid = $(".webapp-div input:checked").attr("cid")
        window.location.href = "hackathon?cid=" + cid
    });
});

