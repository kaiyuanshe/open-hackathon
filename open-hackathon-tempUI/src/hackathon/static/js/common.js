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
var hqg_post_local = function(url, data, success_func, error_func){
     $.ajax({
        url: CONFIG.hackathon.qg_local_endpoint + url,
        type: "POST",
        headers: h_headers,
        data: JSON.stringify(data),
        contentType: "application/json",
        success: success_func,
        error: error_func
    })
}
var gitcafe_post_local = function(url, data, success_func, error_func){
     $.ajax({
        url: CONFIG.hackathon.gitcafe_endpoint + url,
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