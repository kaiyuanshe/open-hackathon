[1mdiff --cc osslab/src/app/templates/third.html[m
[1mindex 4da7113,9b6dcb7..0000000[m
[1m--- a/osslab/src/app/templates/third.html[m
[1m+++ b/osslab/src/app/templates/third.html[m
[36m@@@ -47,14 -12,14 +12,14 @@@[m
          <div class="left">[m
              <div class="left-title">工具栏</div>[m
              <ul>[m
[31m-                 <li><a>Copy</a></li>[m
[31m-                 <li><a>Paste</a></li>[m
[31m-                 <li><a id="new-window" href="#" target="_blank">分离</a></li>[m
[31m-                 <li><a>字+</a></li>[m
[31m-                 <li><a>字-</a></li>[m
[31m-                 <li><a>保存</a></li>[m
[31m-                 <li><a>部署</a></li>[m
[31m-                 <li><a id="third-leave" href="#">stop</a></li>[m
[32m+                 <li><button>Copy</button></li>[m
[32m+                 <li><button>Paste</button></li>[m
[31m -                <li><button>分离</button></li>[m
[32m++                <li><button id="new-window">分离</button></li>[m
[32m+                 <li><button>字+</button></li>[m
[32m+                 <li><button>字-</button></li>[m
[32m+                 <li><button>保存</button></li>[m
[32m+                 <li><button>部署</button></li>[m
[32m+                 <li><button id="third-leave">stop</button></li>[m
              </ul>[m
          </div>[m
          [m
[36m@@@ -91,17 -62,7 +62,11 @@@[m
                      <iframe id="course_vm4" src="/loading" width="100%" height="380px" class="" style="border: 1px solid #000;" frameborder="yes" marginwidth="10" scrolling="yes" onmouseover="setFocusThickboxIframe()" onmousemove = "setFocusThickboxIframe()" onmouseout = "setFocusThickboxIframe()" onfocus = "setFocusThickboxIframe()" onblur = "setFocusThickboxIframe()"></iframe>[m
                  </div>[m
              </div>[m
[32m +[m
[32m +            <div style="padding: 10px">[m
[32m +                <button id="submit" disabled="disabled">submit</button>[m
[32m +            </div>[m
          </div>[m
[31m-         <div class="right">[m
[31m-             <iframe id="rightSide" width="100%" height="880px" src="/rightSide" frameborder="yes"></iframe>[m
[31m-             </div>[m
[31m-         </div>[m
[31m-     </div>[m
[31m-     [m
  <!--    <iframe src="foot.html" width="100%" height="51px" class="navbar-fixed-buttom" style="border: 1px solid #000;"></iframe>-->[m
      {% endblock %}[m
  <!--[m
