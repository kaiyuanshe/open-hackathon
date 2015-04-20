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

function getParameterByName(name){
    name = name.replace(/[\[]/,"\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);

    return results===null?"":decodeURIComponent(results[1].replace(/\+/g, " "));
}

var h_headers = {
    "token": $.cookie("token")
}

var hpost = function(url, data, success_func, error_func){
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
var hpost_local = function(url, data, success_func, error_func){
     $.ajax({
        url: CONFIG.hackathon.local_endpoint + url,
        type: "POST",
        headers: h_headers,
        data: JSON.stringify(data),
        contentType: "application/json",
        success: success_func,
        error: error_func
    })
}
var hget = function(url, success_func, error_func){
    $.ajax({
        url: CONFIG.hackathon.endpoint + url,
        type: "GET",
        headers: h_headers,
        success: success_func,
        error: error_func
    })
}

var hdelete = function(url, success_func, error_func){
    $.ajax({
        url: CONFIG.hackathon.endpoint + url,
        type: "DELETE",
        headers: h_headers,
        success: success_func,
        error: error_func
    })
}

var hput=function(url, data, success_func, error_func){
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

var save_token = function(token){
    $.cookie("token", token)
}

var get_token = function(){
    return $.cookie("token")
}