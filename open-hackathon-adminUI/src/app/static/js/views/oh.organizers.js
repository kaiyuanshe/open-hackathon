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
    var hackathonName = '',
        hackathonID = 0,
        files = [],
        basic_info = undefined ;

    function bindAzurecertList(){
        var currentHackathon = oh.comm.getCurrentHackathon();
        var list = $('#organizerlist');
        oh.api.admin.hackathon.get({
           header:{hackathon_name:currentHackathon.name}
        },function(data){
            if(!data.error){
                basic_info = data.basic_info;
                hackathonID = data.id;
                hackathonName = data.name;
                list.empty().append($('#hackathon_organizer').tmpl(basic_info.organizers ||[],{
                    substring:function(str,length){
                        if(str.length>length){
                            return str.substring(0,length)+'...';
                        }
                        return str;
                    }
                }));
                oh.comm.removeLoading();
            }
        });
    }

    function toggleTable(){
        if($('#organizertable').css('display') == 'none' ){
            $('#organizertable').show();
            $('#organizerform').hide()
        }else{
            $('#organizertable').hide();
            $('#organizerform').show()
        }
    }

    function getFormData(){
        var formData = {
            organizer_name:$.trim($('#organizer_name').val()),
            organizer_url:$('#organizer_url').val(),
            organizer_image:$('#organizer_image').val(),
            organizer_description:$('#organizer_description').val()
         }
        return formData;
    }

    function setFormData(data){
        $('#organizer_name').val(data.organizer_name);
        $('#organizer_url').val(data.organizer_url);
        $('#organizer_image').val(data.organizer_image);
        $('#organizer_description').val(data.organizer_description);
    }

    function getOrganizers(){
        var organizers = [];
        $('#organizertable tbody>tr').each(function(i,tr){
            var data = $(tr).data('tmplItem').data;
            if(data){
                organizers.push($(tr).data('tmplItem').data);
            }
        })
        return organizers;
    }

    function updateOrganizers(basic_info){
        return oh.api.hackathon.put({
            body:{
                id:hackathonID,
                name:hackathonName,
                basic_info:basic_info
            },
            header:{
                hackathon_name:hackathonName
            }
        },function(data){
            if(data.error){
                console.log(data);
            }else{
                bindAzurecertList();
                resetForm();
            }
        });
    }

    function resetForm(){
         $('#organizerform').data('bootstrapValidator').resetForm(true);
         $('#organizer_description').val('');
    }

    function init(){
        var editLi = undefined;
        var currentHackathon = oh.comm.getCurrentHackathon();
        var organizerform = $('#organizerform');
        organizerform.bootstrapValidator()
            .on('success.form.bv', function(e) {
                e.preventDefault();
                var itemData = getFormData();
                if(editLi){
                    editLi.data('tmplItem').data = itemData;
                    basic_info.organizers = getOrganizers();
                }else{
                    basic_info.organizers = getOrganizers();
                    basic_info.organizers.push(itemData);
                }
                updateOrganizers(basic_info).then(function(){
                    toggleTable()
                })
            });

        $('#organizertable').on('click','[data-type="edit"]',function(e){
            editLi = $(this).parents('tr')
            var item = editLi.data('tmplItem').data;
            setFormData(item)
            toggleTable();
        });

        $('[data-type="cancel"]').click(function(e){
            resetForm();
            toggleTable();
        });

        $('[data-type="new"]').click(function(e){
            editLi = undefined;
            toggleTable();
        })

        var confirmModal = $('#confirm_modal').on('show.bs.modal',function(e){
            console.log(e);
            editLi = $(e.relatedTarget).parents('tr');
        }).on('click','[data-type="ok"]',function(e){
            editLi.data('tmplItem').data = undefined;
            basic_info.organizers = getOrganizers();
            updateOrganizers(basic_info);
            confirmModal.modal('hide');
        });

        bindAzurecertList();
    }

    $(function() {
        init();
    })
})(window.jQuery,window.oh);