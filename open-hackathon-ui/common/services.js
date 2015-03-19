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


