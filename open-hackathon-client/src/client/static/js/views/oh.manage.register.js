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

;
(function ($, oh) {
    var currentHackathon = oh.comm.getCurrentHackathon();

    function pageLoad() {
        var list = $('#registe_list');
        oh.api.admin.registration.list.get({
            header: {
                hackathon_name: currentHackathon
            }
        }, function (data) {
            list.empty().append($('#register_list_template').tmpl(data));
            list.find('.editable').editable({
                url: function (params) {
                    var id = $(this).parents('tr').data('tmplItem').data.id;
                    var d = new $.Deferred;
                    oh.api.admin.registration.put({
                        body: {
                            id: id,
                            status: Number(params.value)
                        },
                        header: {
                            hackathon_name: currentHackathon
                        }
                    }, function (data) {
                        if (data.error) {
                            d.reject(data.error.friendly_message)
                        } else {
                            d.resolve();
                        }
                    });
                    return d.promise();
                }
            });
        });

    }

    function deleteuRegister(data) {
        return oh.api.admin.registration.delete(data);
    }

    function init() {
        pageLoad();
        var confirmModal = $('#confirm_modal').on('show.bs.modal', function (e) {
            console.log(e);
            editLi = $(e.relatedTarget).parents('tr');
        }).on('click', '[data-type="ok"]', function (e) {
            var id = editLi.data('tmplItem').data.id;
            confirmModal.modal('hide');
            deleteuRegister({query: {id: id}, header: {hackathon_name: currentHackathon}}).then(function (data) {
                if (data.error) {
                    oh.comm.alert('delete registered user fail: ', data.error.friendly_message);
                } else {
                    editLi.detach();
                }
            });
        });
    }

    $(function () {
        init();
    });
})(jQuery, window.oh);
