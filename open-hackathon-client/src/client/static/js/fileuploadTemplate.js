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
    oh.uploadTemplate ='{% for (var i=0, file; file=o.files[i]; i++) { %}\
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

    oh.downloadTemplate = '{% for (var i=0, file; file=o.files[i]; i++) { %}\
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
                <a class="delete" data-action="close" title="删除" data-type="DELETE" data-url="'+ CONFIG.apiconfig.proxy+'{%=file.deleteUrl%}" {% if (file.deleteWithCredentials) { %} data-xhr-fields="{\"withCredentials\":true}"{% } %}>\
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

})(window.jQuery,window.oh);