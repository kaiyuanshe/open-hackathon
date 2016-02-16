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
