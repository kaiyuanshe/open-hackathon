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

 (function($) {
    $.fn.bootstrapValidator.i18n.remote1 = $.extend($.fn.bootstrapValidator.i18n.remote1 || {}, {
        'default': 'Please enter a valid value'
    });

    $.fn.bootstrapValidator.validators.remote1 = {
        html5Attributes: {
            message: 'message',
            checkfun:'checkfun'
        },
        destroy: function(validator, $field, options) {
            if ($field.data('bv.remote1.timer')) {
                clearTimeout($field.data('bv.remote1.timer'));
                $field.removeData('bv.remote1.timer');
            }
        },
        validate: function(validator, $field, options) {
           return options.checkfun(validator, $field);
        }
    };
}(window.jQuery));

(function($, oh) {

    var daterangepickerLocale = {
        applyLabel: '应用',
        cancelLabel: '取消',
        fromLabel: '从',
        toLabel: '到',
        customRangeLabel: '自定义',
        daysOfWeek: ['日', '一', '二', '三', '四', '五','六'],
        monthNames: ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月'],
        firstDay: 1
    }

    var hackathonName = '', hackathonID = 0;

    var uploadTemplate ='{% for (var i=0, file; file=o.files[i]; i++) { %}\
        <div class="col-sm-3 col-xs-6 template-upload">\
            <div class="thumbnail">\
            <span class="preview">\
            </span>\
            <div class="image-info">\
                <p class="error"></p>\
                <div class="progress progress-striped active" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0">\
                    <div class="progress-bar progress-bar-success" style="width:0%;"></div>\
                </div>\
                {% if (!i && !o.options.autoUpload) { %}\
                    <button class="btn btn-primary start" disabled>\
                        <i class="glyphicon glyphicon-upload"></i>\
                        <span>上传</span>\
                    </button>\
                {% } %}\
            </div>\
            {% if (!i) { %}\
                <a class="cancel" data-action="close" title="删除">\
                    <i class="glyphicon glyphicon-remove"></i>\
                </a>\
            {% } %}\
        </div>\
        </div>\
    {% } %}';

    var downloadTemplate = '{% for (var i=0, file; file=o.files[i]; i++) { %}\
        <div class="col-sm-3 col-xs-6 template-download">\
            <div class="thumbnail">\
            <span class="preview">\
                {% if (file.thumbnailUrl) { %}\
                <a href="{%=file.url%}" title="{%=file.name%}" download="{%=file.name%}" data-gallery><img src="{%=file.thumbnailUrl%}"></a>\
                {% } %}\
                {% if (file.error) { %}\
                <img src="/static/pic/warning_spam_file-512.png">\
                {% } %}\
            </span>\
            <div class="image-info">\
                {% if (file.error) { %}\
                    <p class="error">出错 {%=file.error%}</p>\
                {% } else { %}\
                    <p>{%=file.name%}</p>\
                {% } %}\
            </div>\
            {% if (file.deleteUrl) { %}\
                <a class="delete" data-action="close" title="删除" data-type="DELETE" data-url="'+ apiconfig.proxy+'{%=file.deleteUrl%}" {% if (file.deleteWithCredentials) { %} data-xhr-fields="{\"withCredentials\":true}"{% } %}>\
                    <i class="glyphicon glyphicon-remove"></i>\
                </a>\
            {% } else { %}\
            <a class="cancel" data-action="close" title="删除">\
                <i class="glyphicon glyphicon-remove"></i>\
            </a>\
            {% } %}\
        </div>\
        </div>\
    {% } %}';

    var files = [];

    function addFile(file){
        files.push(file);
    }

    function removeFile(url){
        for(var i in files){
            if(files[i].deleteUrl === url){
                files.splice(i, 1);
                break;
            }
        }
    }

    function getFilesString(){
        var filesUrls = [];
        for(var i in files){
            filesUrls.push(files[i].url);
        }
        return filesUrls.join(';');
    }

    function wizard(step){
        $('.step-content .step-pane').each(function(i,pane){
            if(i+1 == step ){
                $(pane).addClass('active');
               $(pane).find('[type="submit"]').attr({disabled:false});
            }else{
                $(pane).removeClass('active');
            }
        });
    }

    function stepOne(){
        $('#stepform1').bootstrapValidator({
            fields: {
                name: {
                    validators: {
                        remote1: {
                            message:'Hackathon名称已被使用',
                            checkfun:function(validator, $field){
                                var dfd = new $.Deferred();
                                oh.api.hackathon.checkname.get({
                                    query: {
                                        name: $field.val()
                                    }
                                }, function(data) {
                                    var response ={valid:true};
                                    dfd.resolve($field, 'remote1', response);
                                });
                                return dfd;
                            }
                        }
                    }
                }
            }
        }).on('success.form.bv', function(e) {
            e.preventDefault();
            var $form = $(e.target);
            hackathonName = $.trim($('#name').val());
            oh.api.hackathon.post({
                body:{
                    name:hackathonName,
                    display_name:$.trim($('#display_name').val())
                }},
                function(data){
                    if(data.error){
                       $('#stepform1').data('bootstrapValidator')
                          .updateStatus('name', 'INVALID','remote1')
                          .validateField('name');
                    }else{
                        hackathonID = data;
                        wizard(2);
                    }
                });
        });
    }

    function stepTwo(){
        $('#stepform2').bootstrapValidator()
            .on('success.form.bv', function(e) {
                e.preventDefault();
                var $form = $(e.target);
                wizard(3);
            })
    }

    function stepThree(){
        $('#stepform3').bootstrapValidator()
        .on('success.form.bv', function(e) {
            e.preventDefault();
            var $form = $(e.target);
            wizard(4);
        })
        $('#stepform3').fileupload({
            url: apiconfig.proxy+'/api/file',
            autoUpload:true,
            prependFiles:true,
            acceptFileTypes:  /(\.|\/)(gif|jpe?g|png)$/i,
            singleFileUploads: true,
            uploadTemplateId:null,
            downloadTemplateId:null,
            uploadTemplate:tmpl(uploadTemplate),
            downloadTemplate:tmpl(downloadTemplate),
            messages: {
                maxNumberOfFiles: '超过最大文件数',
                acceptFileTypes: '图片文件类型不正确',
                maxFileSize: '文件过大',
                minFileSize: '文件过小'
            },
            add: function (e, data) {
                if (e.isDefaultPrevented()) {
                    return false;
                }
                var $this = $(this),
                    that = $this.data('blueimp-fileupload') ||
                        $this.data('fileupload'),
                    options = that.options;
                data.context = that._renderUpload(data.files)
                    .data('data', data)
                    .addClass('processing');
                options.filesContainer[
                    options.prependFiles ? 'prepend' : 'append'
                ](data.context);
                that._forceReflow(data.context);
                that._transition(data.context);
                data.process(function () {
                    return $this.fileupload('process', data);
                }).always(function () {
                    data.context.each(function (index) {
                        $(this).find('.size').text(
                            that._formatFileSize(data.files[index].size)
                        );
                    }).removeClass('processing');
                    that._renderPreviews(data);
                }).done(function () {
                    data.context.find('.error').hide();
                    data.context.find('.start').prop('disabled', false);
                    if ((that._trigger('added', e, data) !== false) &&
                            (options.autoUpload || data.autoUpload) &&
                            data.autoUpload !== false) {
                        data.submit();
                    }
                }).fail(function () {
                    if (data.files.error) {
                        data.context.each(function (index) {
                            var error = data.files[index].error;
                            if (error) {
                                $(this).find('.error').text(error);
                                $(this).find('.preview').append('<img src="/static/pic/warning_spam_file-512.png">');
                                $(this).find('.progress').hide();
                            }
                        });
                    }
                });
            },
            beforeSend: function(xhr, data) {
                xhr.setRequestHeader('token', $.cookie('token'));
                xhr.setRequestHeader('hackathon_name', hackathonName);
            },
            destroy:function(e,data){
                if (e.isDefaultPrevented()) {
                    return false;
                }
                var that = $(this).data('blueimp-fileupload') ||
                    $(this).data('fileupload'),
                    removeNode = function () {
                        that._transition(data.context).done(
                            function () {
                                $(this).remove();
                                that._trigger('destroyed', e, data);
                            }
                        );
                    };
                if (data.url) {
                    data.dataType = data.dataType || that.options.dataType;
                    data.headers = {
                        token:$.cookie('token'),
                        hackathon_name:hackathonName
                    };
                    $.ajax(data).done(removeNode).fail(function () {
                        that._trigger('destroyfailed', e, data);
                    });
                } else {
                    removeNode();
                }
            }
        }).bind('fileuploaddone', function(e,data){
            addFile(data.result.files[0])

        }).bind('fileuploaddestroy',function(e,data){
            removeFile(data.url)
        });
    }

    function stepFour(){
        $('#event_time').daterangepicker({
            timePicker: true,
            format: 'YYYY/MM/DD hh:mm',
            timePickerIncrement: 30,
            timePicker12Hour: false,
            timePickerSeconds: false,
            locale:daterangepickerLocale
        });
        $('#register_time').daterangepicker({
            timePicker: true,
            format: 'YYYY/MM/DD hh:mm',
            timePickerIncrement: 30,
            timePicker12Hour: false,
            timePickerSeconds: false,
            locale:daterangepickerLocale
        });
        $('#judge_time').daterangepicker({
            timePicker: true,
            format: 'YYYY/MM/DD hh:mm',
            timePickerIncrement: 30,
            timePicker12Hour: false,
            timePickerSeconds: false,
            locale:daterangepickerLocale
        });

        $('#markdownEdit').markdown({
            language:'zh'
        })

        $('#stepform4').bootstrapValidator()
        .on('success.form.bv', function(e) {
            e.preventDefault();
            oh.api.hackathon.put({
                body:getHackthonData(),
                header:{
                    hackathon_name:hackathonName
                }
            },function(data){
                if(data.error){
                    console.log(data);
                }else{
                    wizard(5);
                }
            });
        })
    }


    function getHackthonData(){
        var event_time =  $('#event_time').data('daterangepicker');
        var register_time = $('#register_time').data('daterangepicker');
        var judge_time = $('#judge_time').data('daterangepicker');
        var data = {
            id:hackathonID,
            name:hackathonName,
            description:$('#markdownEdit').val(),
            event_start_time: event_time.oldStartDate.format(),
            event_end_time: event_time.oldEndDate.format(),
            registration_start_time:register_time.oldStartDate.format(),
            registration_end_time:register_time.oldEndDate.format(),
            judge_start_time:judge_time.oldStartDate.format(),
            judge_end_time:judge_time.oldEndDate.format(),
            basic_info:{
                banners:getFilesString(),
                location:$.trim($('#location').val()),
                max_enrollment:$('#max_enrollment').val(),
                wall_time:'',
                auto_approve:$('#auto_approve').is(':checked'),
                recycle_enabled:false,
                organizers: [{
                    organizer_name:$.trim($('#organizer_name').val()),
                    organizer_url:$('#organizer_url').val(),
                    organizer_image:$('#organizer_image').val(),
                    organizer_description:$('#organizer_description').val(),
                }]
            }
        }
        return data;
    }
    function stepFive(){


    }

    function init(){
        stepOne();
        stepTwo();
        stepThree();
        stepFour();
        stepFive();
        $('[data-tostep]').click(function(e){
            wizard($(this).data('tostep'));
        });
    }

    $(function() {
        init();
    })
})(window.jQuery,window.oh);
