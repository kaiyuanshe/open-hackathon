/*
 * Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
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

 ;
(function($, oh) {


    function toggleTable(){
        if($('#adminlisttable').css('display') == 'none' ){
            $('#adminlisttable').show();
            $('#adminform').hide()
        }else{
            $('#adminlisttable').hide();
            $('#adminform').show()
        }
    }


     function getFormData(){
        var formData = {
            email:$.trim($('#admin_email').val())
         }
        return formData;
     }


    // initial table to show admin list
    function pageLoad(){
        var list = $('#hackathon_admin_list');
        var currentHackathon = oh.comm.getCurrentHackathon();
        oh.api.hackathon.admin.list.get({
            header: {
                hackathon_name: currentHackathon.name
            }
        }, function(data) {

            list.empty().append($('#hackathon_admin_list_template').tmpl(data,{getOnline:function(online){
                if(online == 1){
                    return '在线'
                }
                return '下线';
            }}));
            oh.comm.removeLoading();
        });
    }

    // call api to add a admin
    function createAdmin(itemData){
        var currentHackathon = oh.comm.getCurrentHackathon();
        oh.api.hackathon.admin.post({
            body: itemData,
            header: {
                hackathon_name: currentHackathon.name
            }
        }, function(data) {
            if(data.error){
                alert(data.error.message)
                savebtn.removeAttr('disabled');
            }else{
            }
        });
    }

    // initial submit button events
    function forminit(){
        var adminform = $('#adminform');
        adminform.bootstrapValidator()
            .on('success.form.bv', function(e) {
                e.preventDefault();
                var itemData = getFormData();
                createAdmin(basic_info).then(function(){
                    pageLoad()
                    toggleTable()
                })
            });
    }

    function init(){
        pageLoad();
        forminit();

        $('[data-type="new"],[data-type="cancel"]').click(function(e){
            toggleTable();
        })

    }

    $(function() {
        init();
    });

})(jQuery, window.oh);