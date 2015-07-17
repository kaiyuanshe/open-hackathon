/*
 * Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
 *
 * The MIT License (MIT)
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

(function($, oh) {

    function getUrlParam(){
        return {
            hackathon_name: $.getUrlParam('hackathon_name'),
            temp_name : $.getUrlParam('temp_name')
        }
    }

    function createRemotes(data){
        removeLoading();
        var remotes = $('#remotes');
        var tabs = $('#tabs');
        $.each(data.remote_servers,function(i,remote){
            var ifrem = $('<iframe>').attr({
                src: remote.url+'&oh='+$.cookie('token'),
                id: remote.name,
                width: '100%',
                height: '100%',
                frameborder: 'no',
                marginwidth: '0',
                scrolling: 'no',
                class: 'v-hidden'
            }).appendTo(remotes);
            var li = $('<li><a href="#'+ remote.name+'">'+ remote.name +'</a></li>').appendTo(tabs);
        });
        tabs.find('a:eq(0)').trigger('click');
    }

    function showError(error){
        removeLoading();
        var remotes = $('#remotes');
        remotes.append($('<p>').text(JSON.stringify(error)));
    }

    function removeLoading(){
        $('.loading').detach();
        $('.full-main').show();
    }

    function bindEvent(){
        var remotes = $('#remotes').bind('tab',function(e,id){
            remotes.find('iframe').addClass('v-hidden');
            remotes.find(id).removeClass('v-hidden');
        }).on('mouseover', 'iframe', function (e) {
            $(this).focus();
        });

        var tabs = $('#tabs').on('click','a',function(e){
            e.preventDefault();
            var _self = $(this)
            var li = _self .parents('li');
            if(!li.hasClass('active')){
                tabs.find('li').removeClass('active');
                li.addClass('active');
                remotes.trigger('tab',[_self.attr('href')])
            }
        });
    }

    function loadingTemp(){
        var param = getUrlParam();
        oh.api.admin.experiment.post({
            body:{name:param.temp_name},
            header:{hackathon_name:param.hackathon_name}
        },function(data){
            if(data.error){
                showError(data.error);
            }
            else if(data.status == 1){
                setTimeout(loadingTemp,60000);
            }else if(data.status == 2){
                createRemotes(data);
            }
        })
    }

    function init(){
        loadingTemp();
        bindEvent();
    }

    $(function(){
        init();
    });
})(window.jQuery,window.oh);