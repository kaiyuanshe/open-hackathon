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