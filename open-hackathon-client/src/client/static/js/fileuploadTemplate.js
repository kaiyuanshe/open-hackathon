/*
 * This file is covered by the LICENSING file in the root of this project.
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