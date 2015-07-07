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
    var currentHackathon = oh.comm.getCurrentHackathon();

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

    function pageload(){

        oh.api.admin.hackathon.get({
            header:{hackathon_name:currentHackathon}
        },function(data){
            if(!data.error){
                setFormData(data);
                oh.comm.removeLoading();
            }
        });
    }

    function setFormData(data){
        data.basic_info = data.basic_info || {};
        $('#hackathon_switch').val(data.status);
        $('#display_name').val(data.display_name);
        $('#location').val(data.basic_info.location);
        $('#max_enrollment').val(data.basic_info.max_enrollment);
        $('#event_time').val(startTimeAndEndTimeTostring(data.event_start_time,data.event_end_time))
            .daterangepicker({
                timePicker: true,
                format: 'YYYY/MM/DD HH:mm',
                timePickerIncrement: 30,
                timePicker12Hour: false,
                timePickerSeconds: false,
                locale:oh.daterangepickerLocale
            });
        $('#register_time').val(startTimeAndEndTimeTostring(data.registration_start_time,data.registration_end_time))
            .daterangepicker({
                timePicker: true,
                format: 'YYYY/MM/DD HH:mm',
                timePickerIncrement: 30,
                timePicker12Hour: false,
                timePickerSeconds: false,
                locale:oh.daterangepickerLocale
            });
        $('#judge_time').val(startTimeAndEndTimeTostring(data.judge_start_time,data.judge_end_time))
            .daterangepicker({
                timePicker: true,
                format: 'YYYY/MM/DD HH:mm',
                timePickerIncrement: 30,
                timePicker12Hour: false,
                timePickerSeconds: false,
                locale:oh.daterangepickerLocale
            });
        $('#auto_approve').attr({checked:data.basic_info.auto_approve || false});
        $('#alauda_enabled').attr({checked:data.basic_info.alauda_enabled || false});
        $('#markdownEdit').val(data.description);
        basic_info = data.basic_info;
        hackathonID = data.id;
        hackathonName = data.name;
        initFilesData(data.basic_info.banners);
    }

    function initFilesData(banners){
        var images = banners ? banners.split(';') : [];
        $.each(images,function(i,imageUrl){
            var url = new URL(imageUrl);
            files.push({
                deleteUrl: CONFIG.apiconfig.proxy+'/api/admin/file?key='+url.pathname.replace('/images/',''),
                name:url.pathname.split('/').pop(),
                thumbnailUrl:imageUrl,
                url:imageUrl
            })
        });
        $('.files').prepend($('#hackathon_images_temp').tmpl(files));
    }

    function startTimeAndEndTimeTostring(startTime,endTime){
        if(!startTime && !endTime){
            return ''
        }
        return moment(startTime).format('YYYY/MM/DD HH:mm ') + '- ' + moment(endTime).format('YYYY/MM/DD HH:mm');
    }

    function getHackthonData(){
        var event_time =  $('#event_time').data('daterangepicker');
        var register_time = $('#register_time').data('daterangepicker');
        var judge_time = $('#judge_time').data('daterangepicker');
        var data = {
            id:hackathonID,
            name:hackathonName,
            display_name:$('#display_name').val(),
            description:$('#markdownEdit').val(),
            event_start_time: event_time.startDate.format(),
            event_end_time: event_time.endDate.format(),
            registration_start_time:register_time.startDate.format(),
            registration_end_time:register_time.endDate.format(),
            judge_start_time:judge_time.startDate.format(),
            judge_end_time:judge_time.endDate.format(),
            basic_info:{
                banners:getFilesString(),
                location:$.trim($('#location').val()),
                max_enrollment:$('#max_enrollment').val(),
                wall_time:'',
                auto_approve:$('#auto_approve').is(':checked'),
                alauda_enabled:$('#alauda_enabled').is(':checked'),
                recycle_enabled:false,
                organizers: basic_info.organizers
            }
        }
        return data;
    }

    function initControls(){
        $('#editHackathonForm').bootstrapValidator()
        .on('success.form.bv', function(e) {
            e.preventDefault();
            oh.api.admin.hackathon.put({
                body:getHackthonData(),
                header:{
                    hackathon_name:hackathonName
                }
            },function(data){
                if(data.error){
                    console.log(data);
                }else{
                    alert('成功');
                }
            });
        });

        $('#editHackathonForm').fileupload({
            url: CONFIG.apiconfig.proxy+'/api/admin/file',
            autoUpload:true,
            prependFiles:true,
            acceptFileTypes:  /(\.|\/)(gif|jpe?g|png)$/i,
            singleFileUploads: true,
            uploadTemplateId:null,
            downloadTemplateId:null,
            uploadTemplate:tmpl(oh.uploadTemplate),
            downloadTemplate:tmpl(oh.downloadTemplate),
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

        $('#markdownEdit').markdown({
            language:'zh'
        })

        $('#hackathon_switch').change(function(e){
            var status = $(this).val();
            oh.api.admin.hackathon.put({
                body:{
                    id:hackathonID,
                    name:hackathonName,
                    status:status
                },
                header:{
                    hackathon_name:hackathonName
                }
            },function(data){
                if(data.error){
                    console.log(data);
                }
            });
        })
    }

    function init(){
        pageload();
        initControls();
    }

    $(function() {
       init();
    })
})(window.jQuery,window.oh);