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
              }, 3000);
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
      link: function(scope, element, attrs, ngModel) {
        var ck = CKEDITOR.replace(element[0]);
        if (!ngModel) return;

        ck.on('save', function() {
          scope.$apply(function() {
            ngModel.$setViewValue(ck.getData());
          });
        });
        // ck.on('pasteState', function() {
        //   scope.$apply(function() {
        //     ngModel.$setViewValue(ck.getData());
        //   });
        // });
        ck.on('keydown', function(e) {
          console.log(e);
        })
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

  });
