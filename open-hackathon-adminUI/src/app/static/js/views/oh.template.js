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

    function bindTemplateList(){
        var currentHackathon = oh.comm.getCurrentHackathon();
        var list = $('#templatelist');
        oh.api.admin.template.get({
            header:{hackathon_name:currentHackathon.name}
        },
        function(data){
            var index = 0;
            list.empty().append($('#template_item').tmpl(data,{getIndex:function(){ return ++index;}}));
        });
    }

    function init(){
        var currentHackathon = oh.comm.getCurrentHackathon();
        $('#templateform')
            .bootstrapValidator()
            .on('success.form.bv', function(e) {
                e.preventDefault();
                oh.api.admin.template.post({
                    body:{
                        subscription_id: $('#subscription_id').val(),
                        management_host: $('#management_host').val()
                    },
                    query:{},
                    header:{hackathon_name:currentHackathon.name}
                }, function(data){
                    if(data.error){
                        // todo
                    }else{
                        bindTemplateList();
                    }
                })
            })

        var confirm_modal = $('#confirm_modal').on('show.bs.modal',function(e){
            var item = $(e.relatedTarget).parents('tr').data('tmplItem').data;
            confirm_modal.data({item:item});
        }).on('click','[data-type="ok"]',function(e){
            var item = confirm_modal.data('item');
             oh.api.admin.template.delete({
                body:{certificate_id:item.id},
                header:{hackathon_name:currentHackathon.name}
             },
             function(data){
                if(data.error){
                    //todo;
                }else{
                    bindTemplateList();
                    confirm_modal.modal('hide');
                }
             })
        })
    }

    $(function() {
        init();
        bindTemplateList();
    })

})(window.jQuery,window.oh);