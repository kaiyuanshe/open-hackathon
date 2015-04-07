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

var endDate = new Date(2015, 11, 17, 18, 00, 00); //年月日时分秒，月要减去1
function getParameterByName(name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);

    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}

var h_headers = {
    "token": $.cookie("token")
}

var hpost = function(url, data, success_func, error_func) {
    $.ajax({
        url: CONFIG.hackathon.endpoint + url,
        type: "POST",
        headers: h_headers,
        data: JSON.stringify(data),
        contentType: "application/json",
        success: success_func,
        error: error_func
    })
}

var hget = function(url, success_func, error_func) {
    $.ajax({
        cache: false,
        url: CONFIG.hackathon.endpoint + url,
        type: "GET",
        headers: h_headers,
        success: success_func,
        error: error_func
    })
}

var hdelete = function(url, success_func, error_func) {
    $.ajax({
        url: CONFIG.hackathon.endpoint + url,
        type: "DELETE",
        headers: h_headers,
        success: success_func,
        error: error_func
    })
}

var hput = function(url, data, success_func, error_func) {
    $.ajax({
        url: CONFIG.hackathon.endpoint + url,
        type: "PUT",
        headers: h_headers,
        data: JSON.stringify(data),
        contentType: "application/json",
        success: success_func,
        error: error_func
    })
}

var save_token = function(token) {
    $.cookie("token", token)
}

var get_token = function() {
    return $.cookie("token")
}
String.prototype.format = function(args) {
    var result = this;
    if (arguments.length > 0) {
        if (arguments.length == 1 && typeof(args) == 'object') {
            for (var key in args) {
                if (args[key] != undefined) {
                    var reg = new RegExp('({' + key + '})', 'g');
                    result = result.replace(reg, args[key]);
                }
            }
        } else {
            for (var i = 0; i < arguments.length; i++) {
                if (arguments[i] != undefined) {
                    var reg = new RegExp('({[' + i + ']})', 'g');
                    result = result.replace(reg, arguments[i]);
                }
            }
        }
    }
    return result;
};

function Countdown(endTime, callback) {
    var time_end, time_server, time_now_1, time_now_2;
    time_end = endTime;
    time_now_1 = new Date();
    time_now_1 = time_now_1.getTime();
    hget('/api/currenttime', function(data) {
        time_server = data.currenttime;
        time_now_2 = new Date();
        time_now_2 = time_now_2.getTime();
        time_server = time_server + (time_now_2 - time_now_1);
        setTimeout(show_time, 1000);
    })

    function show_time() {
        var timing = {
            day: 0,
            hour: 0,
            minute: 0,
            second: 0,
            distance: 0
        }
        time_server += 1000
        timing.distance = time_end - time_server;
        if (timing.distance > 0) {
            timing.day = Math.floor(timing.distance / 86400000)
            timing.distance -= timing.day * 86400000;
            timing.hour = Math.floor(timing.distance / 3600000)
            timing.distance -= timing.hour * 3600000;
            timing.minute = Math.floor(timing.distance / 60000)
            timing.distance -= timing.minute * 60000;
            timing.second = Math.floor(timing.distance / 1000)
            if (timing.day == 0) {
                timing.day = null
            }
            if (timing.hour == 0 && timing.day == null) {
                timing.hour = null
            }
            if (timing.minute == 0 && timing.hour == null) {
                timing.minute = null
            }
            if (timing.second == 0 && timing.minute == null) {
                timing.second = null
            }
            callback(timing);
            setTimeout(show_time, 1000);
        } else {
            callback(null);
        }
    }
}

function api_stat(callback) {
    hget('/api/hackathon/list?name=' + CONFIG.hackathon.name, function(data) {
        var json = $.parseJSON(data);
        $(document).trigger('tiemer', [json]);
        (function loop() {
            hget('/api/hackathon/stat?hid=' + json.id, function(data) {
                callback(data);
                setTimeout(loop, 60000)
            }, function() {
                callback(null);
            });
        })();
    }, function() {
        callback(null)
    })
}
