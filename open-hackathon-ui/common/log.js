var log4js = require('log4js');

module.exports = (function() {
    var log = {
        connectLogger: function(path) {
            log4js.configure(path, {
                level: log4js.levels.INFO
            });
            return log4js.connectLogger('worker');
        } ,
        worker: function() {
            var filelog = log4js.getLogger('worker');
            return filelog;
        }
    }
    return log;
})();
