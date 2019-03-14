/*
 * This file is covered by the LICENSING file in the root of this project.
 */

(function($, oh) {
    var currentHackathon = oh.comm.getCurrentHackathon();

    function bindAzurecertList(){
        var list = $('#azurecertlist');
        oh.api.admin.azure.get({
            header:{hackathon_name:currentHackathon}
        },
        function(data){
            var index = 0;
            list.empty().append($('#azure_cert_item').tmpl(data,{getIndex:function(){ return ++index;}}));
        });
    }

    function init(){

        $('#azurecertform')
            .bootstrapValidator()
            .on('success.form.bv', function(e) {
                e.preventDefault();
                oh.api.admin.azure.post({
                    body:{
                        subscription_id: $('#subscription_id').val(),
                        management_host: $('#management_host').val()
                    },
                    query:{},
                    header:{hackathon_name:currentHackathon}
                }, function(data){
                    if(data.error){
                        // todo
                    }else{
                        bindAzurecertList();
                    }
                })
            })

        var confirm_modal = $('#confirm_modal').on('show.bs.modal', function(e) {
            var item = $(e.relatedTarget).parents('tr').data('tmplItem').data;
            confirm_modal.data({item:item});
        }).on('click', '[data-type="ok"]', function(e) {
            var item = confirm_modal.data('item');
             oh.api.admin.azure.delete({
                query:{certificate_id:item.id},
                header:{hackathon_name:currentHackathon}
             },
             function(data) {
                if(data.error) {
                    //todo;
                } else {
                    bindAzurecertList();
                    confirm_modal.modal('hide');
                }
             })
        })
    }

    $(function() {
        init();
        bindAzurecertList();
    })

})(window.jQuery,window.oh);