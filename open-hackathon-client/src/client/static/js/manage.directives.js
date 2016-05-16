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

angular.module('oh.directives', [])
  //.directive('navBar', function() {})
  .directive('staticImage', function() {
    return {
      restrict: 'A',
      link: function(scope, element, attrs) {
        if (element.prop('tagName') == 'IMG') {
          element.one('load', function(e) {
            var img = this;
            var FitWidth = parseInt(attrs.maxWidth, 10);
            var FitHeight = parseInt(attrs.maxHeight, 10);
            var image = {
              width: img.naturalWidth || img.width,
              height: img.naturalHeight || img.height
            }
            var height = (image.height * FitWidth) / image.width;
            var width = (image.width * FitHeight) / image.height;
            if (height > FitHeight) {
              var h = (height - FitHeight) / 2;
              img.width = FitWidth;

              if (h < FitHeight) {
                img.style.marginTop = -h + 'px';
              }
            } else {
              img.style.marginLeft = -(width - FitWidth) / 2 + 'px';

              img.height = FitHeight
            }
          });
        }

      }
    }
  })
  .directive('tips', function() {
    return {
      restrict: 'E',
      template: '<div class="tips"></div>',
      replace: true,
      scope: {
        tip: '='
      },
      link: function(scope, element, attrs) {
        scope.$watch(attrs.tip, function(newValue, oldValue) {
          if (newValue) {
            var tip = angular.element('<div class="tip">');
            tip.addClass(newValue.level).text(newValue.content);
            element.append(tip);
            setTimeout(function() {
              tip.addClass('show');
              setTimeout(function() {
                tip.removeClass('show');
                setTimeout(function() {
                  tip.remove();
                }, 500);
              },  newValue.showTime|| 5000);
            }, 1);
          }
        });
      }
    }
  })
  .directive('ckeditor', function() {
    return {
      restrict: 'A',
      require: '?ngModel',
      scope: {
        height: '@',
        width: '@'
      },
      link: function(scope, element, attrs, ngModel) {
        var plugins = ['div', 'colordialog', 'liststyle', 'font', 'colorbutton', 'showblocks', 'justify'];
        var addPlugins = attrs.addPlugins || ''
        plugins.push(addPlugins);
        var ck = CKEDITOR.replace(element[0], {
          width: scope.width || 'auto',
          height: scope.height || 'auto',
          extraPlugins: plugins.join()
        });
        if (!ngModel) return;

        if (addPlugins.search('save') > -1) {
          ck.on('save', function() {
            scope.$apply(function() {
              ngModel.$setViewValue(ck.getData());
              scope.$parent.updateDescription();
            });
          });
        } else {
          ck.on('pasteState', function() {
            scope.$apply(function() {
              ngModel.$setViewValue(ck.getData());
            });
          });
        }

        ck.on('instanceReady', function() {
          ck.setData(ngModel.$viewValue);
        });
      }
    }
  }).directive('keydown', function() {
    return {
      restrict: 'A',
      link: function(scope, element, attrs) {
        element.bind('keydown', function(e) {
          //console.log(e);
        })
      }
    }

  }).directive('dragable', function($document) {
    return {
      restrict: 'A',
      link: function(scope, elm, attrs) {
        var startX, startY, initialMouseX, initialMouseY;
        var parent = elm.parent();
        elm.on('mousedown', function($event) {
          startX = parent.prop('offsetLeft');
          startY = parent.prop('offsetTop');
          initialMouseX = $event.clientX;
          initialMouseY = $event.clientY;
          $document.bind('mousemove', mousemove);
          $document.bind('mouseup', mouseup);
          $document.addClass('cursor-move');
          return false;
        });

        function mousemove($event) {
          var dx = $event.clientX - initialMouseX;
          var dy = $event.clientY - initialMouseY;
          parent.css({
            top: startY + dy + 'px',
            left: startX + dx + 'px'
          });
          return false;
        }

        function mouseup() {
          $document.removeClass('cursor-move');
          $document.unbind('mousemove', mousemove);
          $document.unbind('mouseup', mouseup);
        }
      }
    }
  }).directive('speech', function(speech) {
    return {
      restrict: 'A',
      link: function(scope, elem, attrs) {
        var type = attrs.speechType || 'tip';
        if (attrs.type == 'checkbox') {
          elem.bind('change', function(e) {
            if (e.target.checked) {
              speech.on();
            } else {
              speech.off();
            }
          })
        }
      }
    }
  }).directive('checkValue', function() {
    return {
      restrict: 'A',
      scope: {
        checkChange: '&'
      },

      link: function(scope, elem, attrs) {
        elem.bind('change', function(e) {
          scope.checkChange({'$event': e}); 
        })
      }
    }
  }).directive('fileModel', function ($parse) {
    return {
        restrict: 'A',
        link: function(scope, element, attrs) {
          var model = $parse(attrs.fileModel);
          var modelSetter = model.assign;

          element.bind('change', function(){
            scope.$apply(function(){
              modelSetter(scope, element[0].files[0]);
            });
          });
        }
    };
  });


angular.module("oh.templates", []).run(["$templateCache", function($templateCache) {

  $templateCache.put("manage/template/dialogs/alert.html", '<div class="modal-header cursor-move" dragable>\
  <h3 class="modal-title">\
  <button type="button" class="close" ng-click="cancel()"><span aria-hidden="true">&times;</span></button>\
  {{title}} </h3>\
  </div>\
  <div class="modal-body text-center" ng-bind-html="body">\
  </div>\
  <div class="modal-footer">\
    <button class="btn btn-success btn-sm" type="button" ng-click="ok()" translate="OK">OK</button>\
  </div>');

  $templateCache.put("manage/template/dialogs/confirm.html", '<div class="modal-header cursor-move " dragable>\
  <h3 class="modal-title">\
  <button type="button" class="close" ng-click="cancel()"><span aria-hidden="true">&times;</span></button>\
  {{title}} </h3>\
  </div>\
  <div class="modal-body text-center" ng-bind-html="body">\
  </div>\
  <div class="modal-footer">\
  <button class="btn btn-success btn-sm" type="button" ng-click="ok()" translate="OK">OK</button>\
  <button class="btn btn-default btn-sm" type="button" ng-click="cancel()" translate="CANCEL">CANCEL</button>\
  </div>');

  $templateCache.put("manage/template/dialogs/upimage.html",'<div>updimage</div>');

}]);
