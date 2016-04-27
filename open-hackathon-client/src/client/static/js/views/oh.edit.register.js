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

;
(function($, oh) {
    var currentHackathon = oh.comm.getCurrentHackathon();

    function getParamId(){
        var id = parseInt($.getUrlParam('id') || 0);
        id = isNaN(id) ? 0 : id;
        return id;
    }
    function pageload(){
        var id = getParamId();
        if (id > 0) {
            oh.api.admin.registration.get({ query: { id: id}}, function(data) {
                for (var key in data) {
                    if (key == 'hackathon_id') {
                        editBindHackathons(key, data[key]);
                    } else {
                        var input = $('[data-name="' + key + '"]').text(data[key]).attr({
                            'data-value': data[key]
                        });
                        if(input.is('[required]')){
                            input .editable({
                                validate: function(value) {
                                   if($.trim(value) == '') return input.data('required');
                               }
                            });
                        }else{
                            input .editable();
                        }
                    }
                }
            });
        }else{
            $('.editable').each(function(i,o){
                var input = $(o);
                if(input.is('[required]')){
                    input.editable({
                        validate: function(value) {
                           if($.trim(value) == '') return input.data('required');
                        }
                    });
                }else{
                    input.editable();
                }
            })
        }
    }

    function editBindHackathons(name, value) {
        oh.api.admin.hackathon.list.get(function(hackathons) {
            var source = {};
            $.each(hackathons, function(i, o) {
                source[o.id] = o.name;
            })
            var input = $('[data-name="' + name + '"]').attr({
                'data-source': JSON.stringify(source),
                'data-value': value
            }).text(source[value]).editable({
                validate: function(value) {
                if($.trim(value) == '') return input.data('required');
                }
             });
        });
    }

    function init(){
        pageload();
        var id = getParamId();
        var savebtn = $('#save-btn').click(function() {
            savebtn.attr({
                disabled: 'disabled'
            });
            var data,
                $elems = $('.editable'),
                errors = $elems.editable('validate');
            if ($.isEmptyObject(errors)) {
                data = $elems.editable('getValue');
                if (id > 0) {
                    data.id = id;
                    oh.api.admin.registration.put({
                        body: data,
                        header: {
                            hackathon_name: currentHackathon
                        }
                    }, function(data) {
                        if(data.error){
                            alert(data.error.message)
                            savebtn.removeAttr('disabled');
                        }else{
                            id = data.id;
                            alert('成功');
                        }
                    });
                } else {
                     oh.api.admin.registration.post({
                        body: data,
                        header: {
                            hackathon_name: currentHackathon
                        }
                    }, function(data) {
                        if(data.error){
                            alert(data.error.message);
                            savebtn.removeAttr('disabled');
                        }else{
                            id = data.id
                            location.href = location.pathname + '?id=' + id;
                            alert('成功');
                        }
                    });
                }
            } else {
                savebtn.removeAttr('disabled');
            }
        });
    }

    $(function() {
        init();
    });

})(jQuery, window.oh);
