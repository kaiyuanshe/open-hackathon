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

    // get all templates filter data
    function getFilterData(){
        var Data = {
            name:$.trim($('#template_name').val()),
            status:$.trim($('#status').val()),
            description:$.trim($('#template_description').val())
         }
        return Data;
    }

    // get all templates
    function getTemplateList(){
        var list = $('#alltemplatelist');
        oh.api.template.list.get({
            query: getFilterData()
        }, function(data){
            var index = 0;
            list.empty().append($('#all_template_item').tmpl(data,{
                getIndex:function(){ return ++index;},
                getStatus:function(status){
                    if(status == 1){
                        return '审核通过'
                    }
                    if(status == 2){
                        return '审核失败'
                    }
                    return '未审核';
                },
                getColor:function(status){
                    if(status == 1){
                        return "#ADFEDC"
                    }
                    if(status == 2){
                        return '审核失败'
                    }
                    return '未审核';
                }

            }));
        });
        $('#template_list_filter').find('[data-type="query"]').removeAttr('disabled')
    }


    function init(){
        var templateform = $('#template_list_filter');
        templateform.bootstrapValidator().on('success.form.bv', function(e) {
            e.preventDefault();
            var formData = getFormData();
            (is_update ? updateTemplate(formData) : createTemplate(formData)).then(function(){
                if(is_update)
                    is_update = false;
                bindTemplateList();
                toggleTable();
            })
        });

        templateform.on('click','[data-type="query"]',function(e){
            $(this).attr('disabled','disabled')
            getTemplateList(this);
        });

    }

    $(function() {
        init();
        getTemplateList();
    })

})(window.jQuery,window.oh);