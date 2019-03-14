/*
 * This file is covered by the LICENSING file in the root of this project.
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