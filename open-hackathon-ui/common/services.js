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

var request = require('request');
var config = require('../config');


module.exports = (function () {
  function scan(obj, name) {
    var key;
    var getCmd = {};
    if (obj instanceof Array) {
      for (key in obj) {
        getCmd[obj[key]] = scan(obj[key], name)
      }
      return getCmd;
    } else if (obj instanceof Object) {
      for (key in obj) {
        if (obj.hasOwnProperty(key)) {
          if (key == '_self') {
            getCmd = scan(obj[key], name)
          } else {
            getCmd[key] = scan(obj[key], name + '/' + key);
          }
        }
      }
      return getCmd;
    } else {
      return getCmd[obj] = function (query, headers, callback) {
        if (!callback) {
          callback = headers;
          headers = {};
        }
        var options = {
          method: obj,
          url: name,
          'content-type': 'application/json',
          headers: headers,
          json: query
        }
        request(options, function (err, res, data) {
          callback(res, data);
        })
      }
    }
  }

  return scan(config.api, config.proxy+'/api');
})();


