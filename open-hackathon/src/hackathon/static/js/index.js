/* msopentech-theme 2014-09-05 */
/*
 * hoverFlow - A Solution to Animation Queue Buildup in jQuery
 * Version 1.00
 *
 * Copyright (c) 2009 Ralf Stoltze, http://www.2meter3.de/code/hoverFlow/
 * Dual-licensed under the MIT and GPL licenses.
 * http://www.opensource.org/licenses/mit-license.php
 * http://www.gnu.org/licenses/gpl.html
 */

/*! http://responsiveslides.com v1.54 by @viljamis */
(function(c, I, B) {
    c.fn.responsiveSlides = function(l) {
        var a = c.extend({
            auto: !0,
            speed: 500,
            timeout: 4E3,
            pager: !1,
            nav: !1,
            random: !1,
            pause: !1,
            pauseControls: !0,
            prevText: "Previous",
            nextText: "Next",
            maxwidth: "",
            navContainer: "",
            manualControls: "",
            namespace: "rslides",
            before: c.noop,
            after: c.noop
        }, l);
        return this.each(function() {
            B++;
            var f = c(this),
                s, r, t, m, p, q, n = 0,
                e = f.children(),
                C = e.size(),
                h = parseFloat(a.speed),
                D = parseFloat(a.timeout),
                u = parseFloat(a.maxwidth),
                g = a.namespace,
                d = g + B,
                E = g + "_nav " + d + "_nav",
                v = g + "_here",
                j = d + "_on",
                w = d + "_s",
                k = c("<ul class='" + g + "_tabs " + d + "_tabs' />"),
                x = {
                    "float": "left",
                    position: "relative",
                    opacity: 1,
                    zIndex: 2
                },
                y = {
                    "float": "none",
                    position: "absolute",
                    opacity: 0,
                    zIndex: 1
                },
                F = function() {
                    var b = (document.body || document.documentElement).style,
                        a = "transition";
                    if ("string" === typeof b[a]) return !0;
                    s = ["Moz", "Webkit", "Khtml", "O", "ms"];
                    var a = a.charAt(0).toUpperCase() + a.substr(1),
                        c;
                    for (c = 0; c < s.length; c++)
                        if ("string" === typeof b[s[c] + a]) return !0;
                    return !1
                }(),
                z = function(b) {
                    a.before(b);
                    F ? (e.removeClass(j).css(y).eq(b).addClass(j).css(x),
                        n = b, setTimeout(function() {
                            a.after(b)
                        }, h)) : e.stop().fadeOut(h, function() {
                        c(this).removeClass(j).css(y).css("opacity", 1)
                    }).eq(b).fadeIn(h, function() {
                        c(this).addClass(j).css(x);
                        a.after(b);
                        n = b
                    })
                };
            a.random && (e.sort(function() {
                return Math.round(Math.random()) - 0.5
            }), f.empty().append(e));
            e.each(function(a) {
                this.id = w + a
            });
            f.addClass(g + " " + d);
            l && l.maxwidth && f.css("max-width", u);
            e.hide().css(y).eq(0).addClass(j).css(x).show();
            F && e.show().css({
                "-webkit-transition": "opacity " + h + "ms ease-in-out",
                "-moz-transition": "opacity " +
                    h + "ms ease-in-out",
                "-o-transition": "opacity " + h + "ms ease-in-out",
                transition: "opacity " + h + "ms ease-in-out"
            });
            if (1 < e.size()) {
                if (D < h + 100) return;
                if (a.pager && !a.manualControls) {
                    var A = [];
                    e.each(function(a) {
                        a += 1;
                        A += "<li><a href='#' class='" + w + a + "'>" + a + "</a></li>"
                    });
                    k.append(A);
                    l.navContainer ? c(a.navContainer).append(k) : f.after(k)
                }
                a.manualControls && (k = c(a.manualControls), k.addClass(g + "_tabs " + d + "_tabs"));
                (a.pager || a.manualControls) && k.find("li").each(function(a) {
                    c(this).addClass(w + (a + 1))
                });
                if (a.pager || a.manualControls) q =
                    k.find("a"), r = function(a) {
                        q.closest("li").removeClass(v).eq(a).addClass(v)
                    };
                a.auto && (t = function() {
                    p = setInterval(function() {
                        e.stop(!0, !0);
                        var b = n + 1 < C ? n + 1 : 0;
                        (a.pager || a.manualControls) && r(b);
                        z(b)
                    }, D)
                }, t());
                m = function() {
                    a.auto && (clearInterval(p), t())
                };
                a.pause && f.hover(function() {
                    clearInterval(p)
                }, function() {
                    m()
                });
                if (a.pager || a.manualControls) q.bind("click", function(b) {
                        b.preventDefault();
                        a.pauseControls || m();
                        b = q.index(this);
                        n === b || c("." + j).queue("fx").length || (r(b), z(b))
                    }).eq(0).closest("li").addClass(v),
                    a.pauseControls && q.hover(function() {
                        clearInterval(p)
                    }, function() {
                        m()
                    });
                if (a.nav) {
                    g = "<a href='#' class='" + E + " prev'>" + a.prevText + "</a><a href='#' class='" + E + " next'>" + a.nextText + "</a>";
                    l.navContainer ? c(a.navContainer).append(g) : f.after(g);
                    var d = c("." + d + "_nav"),
                        G = d.filter(".prev");
                    d.bind("click", function(b) {
                        b.preventDefault();
                        b = c("." + j);
                        if (!b.queue("fx").length) {
                            var d = e.index(b);
                            b = d - 1;
                            d = d + 1 < C ? n + 1 : 0;
                            z(c(this)[0] === G[0] ? b : d);
                            if (a.pager || a.manualControls) r(c(this)[0] === G[0] ? b : d);
                            a.pauseControls || m()
                        }
                    });
                    a.pauseControls && d.hover(function() {
                        clearInterval(p)
                    }, function() {
                        m()
                    })
                }
            }
            if ("undefined" === typeof document.body.style.maxWidth && l.maxwidth) {
                var H = function() {
                    f.css("width", "100%");
                    f.width() > u && f.css("width", u)
                };
                H();
                c(I).bind("resize", function() {
                    H()
                })
            }
        })
    }
})(jQuery, this, 0);

/*!
 AnythingSlider v1.9.0 minified using Google Closure Compiler
 Original by Chris Coyier: http://css-tricks.com
 Get the latest version: https://github.com/CSS-Tricks/AnythingSlider
*/
;
(function(d, m, l) {
    d.anythingSlider = function(j, p) {
        var a = this,
            b, k;
        a.el = j;
        a.$el = d(j).addClass("anythingBase").wrap('<div class="anythingSlider"><div class="anythingWindow" /></div>');
        a.$el.data("AnythingSlider", a);
        a.init = function() {
            a.options = b = d.extend({}, d.anythingSlider.defaults, p);
            a.initialized = !1;
            d.isFunction(b.onBeforeInitialize) && a.$el.bind("before_initialize", b.onBeforeInitialize);
            a.$el.trigger("before_initialize", a);
            d('\x3c!--[if lte IE 8]><script>jQuery("body").addClass("as-oldie");\x3c/script><![endif]--\x3e').appendTo("body").remove();
            a.$wrapper = a.$el.parent().closest("div.anythingSlider").addClass("anythingSlider-" + b.theme);
            a.$outer = a.$wrapper.parent();
            a.$window = a.$el.closest("div.anythingWindow");
            a.$win = d(m);
            a.$controls = d('<div class="anythingControls"></div>');
            a.$nav = d('<ul class="thumbNav"><li><a><span></span></a></li></ul>');
            a.$startStop = d('<a href="#" class="start-stop"></a>');
            if (b.buildStartStop || b.buildNavigation) a.$controls.appendTo(b.appendControlsTo && d(b.appendControlsTo).length ? d(b.appendControlsTo) : a.$wrapper);
            b.buildNavigation && a.$nav.appendTo(b.appendNavigationTo && d(b.appendNavigationTo).length ? d(b.appendNavigationTo) : a.$controls);
            b.buildStartStop && a.$startStop.appendTo(b.appendStartStopTo && d(b.appendStartStopTo).length ? d(b.appendStartStopTo) : a.$controls);
            a.runTimes = d(".anythingBase").length;
            a.regex = b.hashTags ? RegExp("panel" + a.runTimes + "-(\\d+)", "i") : null;
            1 === a.runTimes && a.makeActive();
            a.flag = !1;
            b.autoPlayLocked && (b.autoPlay = !0);
            a.playing = b.autoPlay;
            a.slideshow = !1;
            a.hovered = !1;
            a.panelSize = [];
            a.currentPage = a.targetPage = b.startPanel = parseInt(b.startPanel, 10) || 1;
            b.changeBy = parseInt(b.changeBy, 10) || 1;
            k = (b.mode || "h").toLowerCase().match(/(h|v|f)/);
            k = b.vertical ? "v" : (k || ["h"])[0];
            b.mode = "v" === k ? "vertical" : "f" === k ? "fade" : "horizontal";
            "f" === k && (b.showMultiple = 1, b.infiniteSlides = !1);
            a.adj = b.infiniteSlides ? 0 : 1;
            a.adjustMultiple = 0;
            b.playRtl && a.$wrapper.addClass("rtl");
            b.buildStartStop && a.buildAutoPlay();
            b.buildArrows && a.buildNextBackButtons();
            a.$lastPage = a.$targetPage = a.$currentPage;
            a.updateSlider();
            b.expand && (a.$window.css({
                width: "100%",
                height: "100%"
            }), a.checkResize());
            d.isFunction(d.easing[b.easing]) || (b.easing = "swing");
            b.pauseOnHover && a.$wrapper.hover(function() {
                a.playing && (a.$el.trigger("slideshow_paused", a), a.clearTimer(!0))
            }, function() {
                a.playing && (a.$el.trigger("slideshow_unpaused", a), a.startStop(a.playing, !0))
            });
            a.slideControls(!1);
            a.$wrapper.bind("mouseenter mouseleave", function(b) {
                d(this)["mouseenter" === b.type ? "addClass" : "removeClass"]("anythingSlider-hovered");
                a.hovered = "mouseenter" === b.type ? !0 : !1;
                a.slideControls(a.hovered)
            });
            d(l).keyup(function(c) {
                if (b.enableKeyboard && (a.$wrapper.hasClass("activeSlider") && !c.target.tagName.match("TEXTAREA|INPUT|SELECT")) && !("vertical" !== b.mode && (38 === c.which || 40 === c.which))) switch (c.which) {
                    case 39:
                    case 40:
                        a.goForward();
                        break;
                    case 37:
                    case 38:
                        a.goBack()
                }
            });
            a.currentPage = (b.hashTags ? a.gotoHash() : "") || b.startPanel || 1;
            a.gotoPage(a.currentPage, !1, null, -1);
            var c = "slideshow_paused slideshow_unpaused slide_init slide_begin slideshow_stop slideshow_start initialized swf_completed".split(" ");
            d.each("onShowPause onShowUnpause onSlideInit onSlideBegin onShowStop onShowStart onInitialized onSWFComplete".split(" "), function(f, e) {
                d.isFunction(b[e]) && a.$el.bind(c[f], b[e])
            });
            d.isFunction(b.onSlideComplete) && a.$el.bind("slide_complete", function() {
                setTimeout(function() {
                    b.onSlideComplete(a)
                }, 0);
                return !1
            });
            a.initialized = !0;
            a.$el.trigger("initialized", a);
            a.startStop(b.autoPlay)
        };
        a.updateSlider = function() {
            a.$el.children(".cloned").remove();
            a.navTextVisible = "hidden" !== a.$nav.find("span:first").css("visibility");
            a.$nav.empty();
            a.currentPage = a.currentPage || 1;
            a.$items = a.$el.children();
            a.pages = a.$items.length;
            a.dir = "vertical" === b.mode ? "top" : "left";
            b.showMultiple = parseInt(b.showMultiple, 10) || 1;
            b.navigationSize = !1 === b.navigationSize ? 0 : parseInt(b.navigationSize, 10) || 0;
            a.$items.find("a").unbind("focus.AnythingSlider").bind("focus.AnythingSlider", function(c) {
                var f = d(this).closest(".panel"),
                    f = a.$items.index(f) + a.adj;
                a.$items.find(".focusedLink").removeClass("focusedLink");
                d(this).addClass("focusedLink");
                a.$window.scrollLeft(0).scrollTop(0);
                if (-1 !== f && (f >= a.currentPage + b.showMultiple || f < a.currentPage)) a.gotoPage(f), c.preventDefault()
            });
            1 < b.showMultiple && (b.showMultiple > a.pages && (b.showMultiple = a.pages), a.adjustMultiple = b.infiniteSlides && 1 < a.pages ? 0 : b.showMultiple - 1);
            a.$controls.add(a.$nav).add(a.$startStop).add(a.$forward).add(a.$back)[1 >= a.pages ? "hide" : "show"]();
            1 < a.pages && a.buildNavigation();
            "fade" !== b.mode && (b.infiniteSlides && 1 < a.pages) && (a.$el.prepend(a.$items.filter(":last").clone().addClass("cloned")), 1 < b.showMultiple ? a.$el.append(a.$items.filter(":lt(" + b.showMultiple + ")").clone().addClass("cloned multiple")) : a.$el.append(a.$items.filter(":first").clone().addClass("cloned")), a.$el.find(".cloned").each(function() {
                d(this).find("a,input,textarea,select,button,area,form").attr({
                    disabled: "disabled",
                    name: ""
                });
                d(this).find("[id]")[d.fn.addBack ? "addBack" : "andSelf"]().removeAttr("id")
            }));
            a.$items = a.$el.addClass(b.mode).children().addClass("panel");
            a.setDimensions();
            b.resizeContents ? (a.$items.css("width", a.width), a.$wrapper.css("width", a.getDim(a.currentPage)[0]).add(a.$items).css("height", a.height)) : a.$win.load(function() {
                a.setDimensions();
                k = a.getDim(a.currentPage);
                a.$wrapper.css({
                    width: k[0],
                    height: k[1]
                });
                a.setCurrentPage(a.currentPage, !1)
            });
            a.currentPage > a.pages && (a.currentPage = a.pages);
            a.setCurrentPage(a.currentPage, !1);
            a.$nav.find("a").eq(a.currentPage - 1).addClass("cur");
            "fade" === b.mode && (k = a.$items.eq(a.currentPage - 1), b.resumeOnVisible ? k.css({
                opacity: 1
            }).siblings().css({
                opacity: 0
            }) : (a.$items.css("opacity", 1), k.fadeIn(0).siblings().fadeOut(0)))
        };
        a.buildNavigation = function() {
            if (b.buildNavigation && 1 < a.pages) {
                var c, f, e, g, h;
                a.$items.filter(":not(.cloned)").each(function(n) {
                    h = d("<li/>");
                    e = n + 1;
                    f = (1 === e ? " first" : "") + (e === a.pages ? " last" : "");
                    c = '<a class="panel' + e + (a.navTextVisible ? '"' : " " + b.tooltipClass + '" title="@"') + ' href="#"><span>@</span></a>';
                    d.isFunction(b.navigationFormatter) ? (g = b.navigationFormatter(e, d(this)), "string" === typeof g ? h.html(c.replace(/@/g, g)) : h = d("<li/>", g)) : h.html(c.replace(/@/g, e));
                    h.appendTo(a.$nav).addClass(f).data("index", e)
                });
                a.$nav.children("li").bind(b.clickControls, function(c) {
                    !a.flag && b.enableNavigation && (a.flag = !0, setTimeout(function() {
                        a.flag = !1
                    }, 100), a.gotoPage(d(this).data("index")));
                    c.preventDefault()
                });
                b.navigationSize && b.navigationSize < a.pages && (a.$controls.find(".anythingNavWindow").length || a.$nav.before('<ul><li class="prev"><a href="#"><span>' + b.backText + "</span></a></li></ul>").after('<ul><li class="next"><a href="#"><span>' + b.forwardText + "</span></a></li></ul>").wrap('<div class="anythingNavWindow"></div>'), a.navWidths = a.$nav.find("li").map(function() {
                    return d(this).outerWidth(!0) + Math.ceil(parseInt(d(this).find("span").css("left"), 10) / 2 || 0)
                }).get(), a.navLeft = a.currentPage, a.$nav.width(a.navWidth(1, a.pages + 1) + 25), a.$controls.find(".anythingNavWindow").width(a.navWidth(1, b.navigationSize + 1)).end().find(".prev,.next").bind(b.clickControls, function(c) {
                    a.flag || (a.flag = !0, setTimeout(function() {
                        a.flag = !1
                    }, 200), a.navWindow(a.navLeft + b.navigationSize * (d(this).is(".prev") ? -1 : 1)));
                    c.preventDefault()
                }))
            }
        };
        a.navWidth = function(b, f) {
            var e;
            e = Math.min(b, f);
            for (var d = Math.max(b, f), h = 0; e < d; e++) h += a.navWidths[e - 1] || 0;
            return h
        };
        a.navWindow = function(c) {
            if (b.navigationSize && b.navigationSize < a.pages && a.navWidths) {
                var f = a.pages - b.navigationSize + 1;
                c = 1 >= c ? 1 : 1 < c && c < f ? c : f;
                c !== a.navLeft && (a.$controls.find(".anythingNavWindow").animate({
                    scrollLeft: a.navWidth(1, c),
                    width: a.navWidth(c, c + b.navigationSize)
                }, {
                    queue: !1,
                    duration: b.animationTime
                }), a.navLeft = c)
            }
        };
        a.buildNextBackButtons = function() {
            a.$forward = d('<span class="arrow forward"><a href="#"><span>' + b.forwardText + "</span></a></span>");
            a.$back = d('<span class="arrow back"><a href="#"><span>' + b.backText + "</span></a></span>");
            a.$back.bind(b.clickBackArrow, function(c) {
                b.enableArrows && !a.flag && (a.flag = !0, setTimeout(function() {
                    a.flag = !1
                }, 100), a.goBack());
                c.preventDefault()
            });
            a.$forward.bind(b.clickForwardArrow, function(c) {
                b.enableArrows && !a.flag && (a.flag = !0, setTimeout(function() {
                    a.flag = !1
                }, 100), a.goForward());
                c.preventDefault()
            });
            a.$back.add(a.$forward).find("a").bind("focusin focusout", function() {
                d(this).toggleClass("hover")
            });
            a.$back.appendTo(b.appendBackTo && d(b.appendBackTo).length ? d(b.appendBackTo) : a.$wrapper);
            a.$forward.appendTo(b.appendForwardTo && d(b.appendForwardTo).length ? d(b.appendForwardTo) : a.$wrapper);
            a.arrowWidth = a.$forward.width();
            a.arrowRight = parseInt(a.$forward.css("right"), 10);
            a.arrowLeft = parseInt(a.$back.css("left"), 10)
        };
        a.buildAutoPlay = function() {
            a.$startStop.html("<span>" + (a.playing ? b.stopText : b.startText) + "</span>").bind(b.clickSlideshow, function(c) {
                b.enableStartStop && (a.startStop(!a.playing), a.makeActive(), a.playing && !b.autoPlayDelayed && a.goForward(!0, b.playRtl));
                c.preventDefault()
            }).bind("focusin focusout", function() {
                d(this).toggleClass("hover")
            })
        };
        a.checkResize = function(b) {
            var f = !(!l.hidden && !l.webkitHidden && !l.mozHidden && !l.msHidden);
            clearTimeout(a.resizeTimer);
            a.resizeTimer = setTimeout(function() {
                var e = a.$outer.width(),
                    d = "BODY" === a.$outer[0].tagName ? a.$win.height() : a.$outer.height();
                if (!f && (a.lastDim[0] !== e || a.lastDim[1] !== d)) a.setDimensions(), a.gotoPage(a.currentPage, a.playing, null, -1);
                "undefined" === typeof b && a.checkResize()
            }, f ? 2E3 : 500)
        };
        a.setDimensions = function() {
            a.$wrapper.find(".anythingWindow, .anythingBase, .panel")[d.fn.addBack ? "addBack" : "andSelf"]().css({
                width: "",
                height: ""
            });
            a.width = a.$el.width();
            a.height = a.$el.height();
            a.outerPad = [a.$wrapper.innerWidth() - a.$wrapper.width(), a.$wrapper.innerHeight() - a.$wrapper.height()];
            var c, f, e, g, h = 0,
                n = {
                    width: "100%",
                    height: "100%"
                },
                j = 1 < b.showMultiple && "horizontal" === b.mode ? a.width || a.$window.width() / b.showMultiple : a.$window.width(),
                k = 1 < b.showMultiple && "vertical" === b.mode ? a.height / b.showMultiple || a.$window.height() / b.showMultiple : a.$window.height();
            b.expand && (a.lastDim = [a.$outer.width(), a.$outer.height()], c = a.lastDim[0] - a.outerPad[0], f = a.lastDim[1] - a.outerPad[1], a.$wrapper.add(a.$window).css({
                width: c,
                height: f
            }), a.height = f = 1 < b.showMultiple && "vertical" === b.mode ? k : f, a.width = j = 1 < b.showMultiple && "horizontal" === b.mode ? c / b.showMultiple : c, a.$items.css({
                width: j,
                height: k
            }));
            a.$items.each(function(k) {
                g = d(this);
                e = g.children();
                b.resizeContents ? (c = a.width, f = a.height, g.css({
                    width: c,
                    height: f
                }), e.length && ("EMBED" === e[0].tagName && e.attr(n), "OBJECT" === e[0].tagName && e.find("embed").attr(n), 1 === e.length && e.css(n))) : ("vertical" === b.mode ? (c = g.css("display", "inline-block").width(), g.css("display", "")) : c = g.width() || a.width, 1 === e.length && c >= j && (c = e.width() >= j ? j : e.width(), e.css("max-width", c)), g.css({
                    width: c,
                    height: ""
                }), f = 1 === e.length ? e.outerHeight(!0) : g.height(), f <= a.outerPad[1] && (f = a.height), g.css("height", f));
                a.panelSize[k] = [c, f, h];
                h += "vertical" === b.mode ? f : c
            });
            a.$el.css("vertical" === b.mode ? "height" : "width", "fade" === b.mode ? a.width : h)
        };
        a.getDim = function(c) {
            var f, e, d = a.width,
                h = a.height;
            if (1 > a.pages || isNaN(c)) return [d, h];
            c = b.infiniteSlides && 1 < a.pages ? c : c - 1;
            if (e = a.panelSize[c]) d = e[0] || d, h = e[1] || h;
            if (1 < b.showMultiple)
                for (e = 1; e < b.showMultiple; e++) f = c + e, "vertical" === b.mode ? (d = Math.max(d, a.panelSize[f][0]), h += a.panelSize[f][1]) : (d += a.panelSize[f][0], h = Math.max(h, a.panelSize[f][1]));
            return [d, h]
        };
        a.goForward = function(c, d) {
            a.gotoPage(a[b.allowRapidChange ? "targetPage" : "currentPage"] + b.changeBy * (d ? -1 : 1), c)
        };
        a.goBack = function(c) {
            a.gotoPage(a[b.allowRapidChange ? "targetPage" : "currentPage"] - b.changeBy, c)
        };
        a.gotoPage = function(c, f, e, g) {
            !0 !== f && (f = !1, a.startStop(!1), a.makeActive());
            /^[#|.]/.test(c) && d(c).length && (c = d(c).closest(".panel").index() + a.adj);
            if (1 !== b.changeBy) {
                var h = a.pages - a.adjustMultiple;
                1 > c && (c = b.stopAtEnd ? 1 : b.infiniteSlides ? a.pages + c : b.showMultiple > 1 - c ? 1 : h);
                c > a.pages ? c = b.stopAtEnd ? a.pages : b.showMultiple > 1 - c ? 1 : c -= h : c >= h && (c = h)
            }
            if (!(1 >= a.pages) && (a.$lastPage = a.$currentPage, "number" !== typeof c && (c = parseInt(c, 10) || b.startPanel, a.setCurrentPage(c)), !f || !b.isVideoPlaying(a))) b.stopAtEnd && (!b.infiniteSlides && c > a.pages - b.showMultiple) && (c = a.pages - b.showMultiple + 1), a.exactPage = c, c > a.pages + 1 - a.adj && (c = !b.infiniteSlides && !b.stopAtEnd ? 1 : a.pages), c < a.adj && (c = !b.infiniteSlides && !b.stopAtEnd ? a.pages : 1), b.infiniteSlides || (a.exactPage = c), a.currentPage = c > a.pages ? a.pages : 1 > c ? 1 : a.currentPage, a.$currentPage = a.$items.eq(a.currentPage - a.adj), a.targetPage = 0 === c ? a.pages : c > a.pages ? 1 : c, a.$targetPage = a.$items.eq(a.targetPage - a.adj), g = "undefined" !== typeof g ? g : b.animationTime, 0 <= g && a.$el.trigger("slide_init", a), 0 < g && a.slideControls(!0), b.buildNavigation && a.setNavigation(a.targetPage), !0 !== f && (f = !1), (!f || b.stopAtEnd && c === a.pages) && a.startStop(!1), 0 <= g && a.$el.trigger("slide_begin", a), setTimeout(function(d) {
                var f, h = !0;
                b.allowRapidChange && a.$wrapper.add(a.$el).add(a.$items).stop(!0, !0);
                b.resizeContents || (f = a.getDim(c), d = {}, a.$wrapper.width() !== f[0] && (d.width = f[0] || a.width, h = !1), a.$wrapper.height() !== f[1] && (d.height = f[1] || a.height, h = !1), h || a.$wrapper.filter(":not(:animated)").animate(d, {
                    queue: !1,
                    duration: 0 > g ? 0 : g,
                    easing: b.easing
                }));
                "fade" === b.mode ? a.$lastPage[0] !== a.$targetPage[0] ? (a.fadeIt(a.$lastPage, 0, g), a.fadeIt(a.$targetPage, 1, g, function() {
                    a.endAnimation(c, e, g)
                })) : a.endAnimation(c, e, g) : (d = {}, d[a.dir] = -a.panelSize[b.infiniteSlides && 1 < a.pages ? c : c - 1][2], "vertical" === b.mode && !b.resizeContents && (d.width = f[0]), a.$el.filter(":not(:animated)").animate(d, {
                    queue: !1,
                    duration: 0 > g ? 0 : g,
                    easing: b.easing,
                    complete: function() {
                        a.endAnimation(c, e, g)
                    }
                }))
            }, parseInt(b.delayBeforeAnimate, 10) || 0)
        };
        a.endAnimation = function(c, d, e) {
            0 === c ? (a.$el.css(a.dir, "fade" === b.mode ? 0 : -a.panelSize[a.pages][2]), c = a.pages) : c > a.pages && (a.$el.css(a.dir, "fade" === b.mode ? 0 : -a.panelSize[1][2]), c = 1);
            a.exactPage = c;
            a.setCurrentPage(c, !1);
            "fade" === b.mode && a.fadeIt(a.$items.not(":eq(" + (c - a.adj) + ")"), 0, 0);
            a.hovered || a.slideControls(!1);
            b.hashTags && a.setHash(c);
            0 <= e && a.$el.trigger("slide_complete", a);
            "function" === typeof d && d(a);
            b.autoPlayLocked && !a.playing && setTimeout(function() {
                a.startStop(!0)
            }, b.resumeDelay - (b.autoPlayDelayed ? b.delay : 0))
        };
        a.fadeIt = function(a, d, e, g) {
            e = 0 > e ? 0 : e;
            if (b.resumeOnVisible) a.filter(":not(:animated)").fadeTo(e, d, g);
            else a.filter(":not(:animated)")[0 === d ? "fadeOut" : "fadeIn"](e, g)
        };
        a.setCurrentPage = function(c, d) {
            c = parseInt(c, 10);
            if (!(1 > a.pages || 0 === c || isNaN(c))) {
                c > a.pages + 1 - a.adj && (c = a.pages - a.adj);
                c < a.adj && (c = 1);
                b.buildArrows && (!b.infiniteSlides && b.stopAtEnd) && (a.$forward[c === a.pages - a.adjustMultiple ? "addClass" : "removeClass"]("disabled"), a.$back[1 === c ? "addClass" : "removeClass"]("disabled"), c === a.pages && a.playing && a.startStop());
                if (!d) {
                    var e = a.getDim(c);
                    a.$wrapper.css({
                        width: e[0],
                        height: e[1]
                    }).add(a.$window).scrollLeft(0).scrollTop(0);
                    a.$el.css(a.dir, "fade" === b.mode ? 0 : -a.panelSize[b.infiniteSlides && 1 < a.pages ? c : c - 1][2])
                }
                a.currentPage = c;
                a.$currentPage = a.$items.removeClass("activePage").eq(c - a.adj).addClass("activePage");
                b.buildNavigation && a.setNavigation(c)
            }
        };
        a.setNavigation = function(b) {
            a.$nav.find(".cur").removeClass("cur").end().find("a").eq(b - 1).addClass("cur")
        };
        a.makeActive = function() {
            a.$wrapper.hasClass("activeSlider") || (d(".activeSlider").removeClass("activeSlider"), a.$wrapper.addClass("activeSlider"))
        };
        a.gotoHash = function() {
            var c = m.location.hash,
                f = c.indexOf("&"),
                e = c.match(a.regex);
            null === e && !/^#&/.test(c) && !/#!?\//.test(c) && !/\=/.test(c) ? (c = c.substring(0, 0 <= f ? f : c.length), e = d(c).length && d(c).closest(".anythingBase")[0] === a.el ? a.$items.index(d(c).closest(".panel")) + a.adj : null) : null !== e && (e = b.hashTags ? parseInt(e[1], 10) : null);
            return e
        };
        a.setHash = function(b) {
            var d = "panel" + a.runTimes + "-",
                e = m.location.hash;
            "undefined" !== typeof e && (m.location.hash = 0 < e.indexOf(d) ? e.replace(a.regex, d + b) : e + "&" + d + b)
        };
        a.slideControls = function(c) {
            var d = c ? 0 : b.animationTime,
                e = c ? b.animationTime : 0,
                g = c ? 1 : 0,
                h = c ? 0 : 1;
            b.toggleControls && a.$controls.stop(!0, !0).delay(d)[c ? "slideDown" : "slideUp"](b.animationTime / 2).delay(e);
            b.buildArrows && b.toggleArrows && (!a.hovered && a.playing && (h = 1, g = 0), a.$forward.stop(!0, !0).delay(d).animate({
                right: a.arrowRight + h * a.arrowWidth,
                opacity: g
            }, b.animationTime / 2), a.$back.stop(!0, !0).delay(d).animate({
                left: a.arrowLeft + h * a.arrowWidth,
                opacity: g
            }, b.animationTime / 2))
        };
        a.clearTimer = function(b) {
            a.timer && (m.clearInterval(a.timer), !b && a.slideshow && (a.$el.trigger("slideshow_stop", a), a.slideshow = !1))
        };
        a.startStop = function(c, d) {
            !0 !== c && (c = !1);
            if ((a.playing = c) && !d) a.$el.trigger("slideshow_start", a), a.slideshow = !0;
            b.buildStartStop && (a.$startStop.toggleClass("playing", c).find("span").html(c ? b.stopText : b.startText), "hidden" === a.$startStop.find("span").css("visibility") && a.$startStop.addClass(b.tooltipClass).attr("title", c ? b.stopText : b.startText));
            c ? (a.clearTimer(!0), a.timer = m.setInterval(function() {
                l.hidden || l.webkitHidden || l.mozHidden || l.msHidden ? b.autoPlayLocked || a.startStop() : b.isVideoPlaying(a) ? b.resumeOnVideoEnd || a.startStop() : a.goForward(!0, b.playRtl)
            }, b.delay)) : a.clearTimer()
        };
        a.init()
    };
    d.anythingSlider.defaults = {
        theme: "default",
        mode: "horiz",
        expand: !1,
        resizeContents: !0,
        showMultiple: !1,
        easing: "swing",
        buildArrows: !0,
        buildNavigation: !0,
        buildStartStop: !0,
        toggleArrows: !1,
        toggleControls: !1,
        startText: "Start",
        stopText: "Stop",
        forwardText: "&raquo;",
        backText: "&laquo;",
        tooltipClass: "tooltip",
        enableArrows: !0,
        enableNavigation: !0,
        enableStartStop: !0,
        enableKeyboard: !0,
        startPanel: 1,
        changeBy: 1,
        hashTags: !0,
        infiniteSlides: !0,
        navigationFormatter: null,
        navigationSize: !1,
        autoPlay: !1,
        autoPlayLocked: !1,
        autoPlayDelayed: !1,
        pauseOnHover: !0,
        stopAtEnd: !1,
        playRtl: !1,
        delay: 3E3,
        resumeDelay: 15E3,
        animationTime: 600,
        delayBeforeAnimate: 0,
        clickForwardArrow: "click",
        clickBackArrow: "click",
        clickControls: "click focusin",
        clickSlideshow: "click",
        allowRapidChange: !1,
        resumeOnVideoEnd: !0,
        resumeOnVisible: !0,
        isVideoPlaying: function() {
            return !1
        }
    };
    d.fn.anythingSlider = function(j, l) {
        return this.each(function() {
            var a, b = d(this).data("AnythingSlider");
            (typeof j).match("object|undefined") ? b ? b.updateSlider() : new d.anythingSlider(this, j) : /\d/.test(j) && !isNaN(j) && b ? (a = "number" === typeof j ? j : parseInt(d.trim(j), 10), 1 <= a && a <= b.pages && b.gotoPage(a, !1, l)) : /^[#|.]/.test(j) && d(j).length && b.gotoPage(j, !1, l)
        })
    }
})(jQuery, window, document);


/* msopentech-theme 2014-09-05 */
window.Modernizr = function(a, b, c) {
        function d(a) {
            t.cssText = a
        }

        function e(a, b) {
            return d(x.join(a + ";") + (b || ""))
        }

        function f(a, b) {
            return typeof a === b
        }

        function g(a, b) {
            return !!~("" + a).indexOf(b)
        }

        function h(a, b) {
            for (var d in a) {
                var e = a[d];
                if (!g(e, "-") && t[e] !== c) return "pfx" == b ? e : !0
            }
            return !1
        }

        function i(a, b, d) {
            for (var e in a) {
                var g = b[a[e]];
                if (g !== c) return d === !1 ? a[e] : f(g, "function") ? g.bind(d || b) : g
            }
            return !1
        }

        function j(a, b, c) {
            var d = a.charAt(0).toUpperCase() + a.slice(1),
                e = (a + " " + z.join(d + " ") + d).split(" ");
            return f(b, "string") || f(b, "undefined") ? h(e, b) : (e = (a + " " + A.join(d + " ") + d).split(" "), i(e, b, c))
        }

        function k() {
            o.input = function(c) {
                for (var d = 0, e = c.length; e > d; d++) E[c[d]] = !!(c[d] in u);
                return E.list && (E.list = !(!b.createElement("datalist") || !a.HTMLDataListElement)), E
            }("autocomplete autofocus list placeholder max min multiple pattern required step".split(" ")), o.inputtypes = function(a) {
                for (var d, e, f, g = 0, h = a.length; h > g; g++) u.setAttribute("type", e = a[g]), d = "text" !== u.type, d && (u.value = v, u.style.cssText = "position:absolute;visibility:hidden;", /^range$/.test(e) && u.style.WebkitAppearance !== c ? (q.appendChild(u), f = b.defaultView, d = f.getComputedStyle && "textfield" !== f.getComputedStyle(u, null).WebkitAppearance && 0 !== u.offsetHeight, q.removeChild(u)) : /^(search|tel)$/.test(e) || (d = /^(url|email)$/.test(e) ? u.checkValidity && u.checkValidity() === !1 : u.value != v)), D[a[g]] = !!d;
                return D
            }("search tel url email datetime date month week time datetime-local number range color".split(" "))
        }
        var l, m, n = "2.7.1",
            o = {},
            p = !0,
            q = b.documentElement,
            r = "modernizr",
            s = b.createElement(r),
            t = s.style,
            u = b.createElement("input"),
            v = ":)",
            w = {}.toString,
            x = " -webkit- -moz- -o- -ms- ".split(" "),
            y = "Webkit Moz O ms",
            z = y.split(" "),
            A = y.toLowerCase().split(" "),
            B = {
                svg: "http://www.w3.org/2000/svg"
            },
            C = {},
            D = {},
            E = {},
            F = [],
            G = F.slice,
            H = function(a, c, d, e) {
                var f, g, h, i, j = b.createElement("div"),
                    k = b.body,
                    l = k || b.createElement("body");
                if (parseInt(d, 10))
                    for (; d--;) h = b.createElement("div"), h.id = e ? e[d] : r + (d + 1), j.appendChild(h);
                return f = ["&#173;", '<style id="s', r, '">', a, "</style>"].join(""), j.id = r, (k ? j : l).innerHTML += f, l.appendChild(j), k || (l.style.background = "", l.style.overflow = "hidden", i = q.style.overflow, q.style.overflow = "hidden", q.appendChild(l)), g = c(j, a), k ? j.parentNode.removeChild(j) : (l.parentNode.removeChild(l), q.style.overflow = i), !!g
            },
            I = function(b) {
                var c = a.matchMedia || a.msMatchMedia;
                if (c) return c(b).matches;
                var d;
                return H("@media " + b + " { #" + r + " { position: absolute; } }", function(b) {
                    d = "absolute" == (a.getComputedStyle ? getComputedStyle(b, null) : b.currentStyle).position
                }), d
            },
            J = function() {
                function a(a, e) {
                    e = e || b.createElement(d[a] || "div"), a = "on" + a;
                    var g = a in e;
                    return g || (e.setAttribute || (e = b.createElement("div")), e.setAttribute && e.removeAttribute && (e.setAttribute(a, ""), g = f(e[a], "function"), f(e[a], "undefined") || (e[a] = c), e.removeAttribute(a))), e = null, g
                }
                var d = {
                    select: "input",
                    change: "input",
                    submit: "form",
                    reset: "form",
                    error: "img",
                    load: "img",
                    abort: "img"
                };
                return a
            }(),
            K = {}.hasOwnProperty;
        m = f(K, "undefined") || f(K.call, "undefined") ? function(a, b) {
            return b in a && f(a.constructor.prototype[b], "undefined")
        } : function(a, b) {
            return K.call(a, b)
        }, Function.prototype.bind || (Function.prototype.bind = function(a) {
            var b = this;
            if ("function" != typeof b) throw new TypeError;
            var c = G.call(arguments, 1),
                d = function() {
                    if (this instanceof d) {
                        var e = function() {};
                        e.prototype = b.prototype;
                        var f = new e,
                            g = b.apply(f, c.concat(G.call(arguments)));
                        return Object(g) === g ? g : f
                    }
                    return b.apply(a, c.concat(G.call(arguments)))
                };
            return d
        }), C.flexbox = function() {
            return j("flexWrap")
        }, C.flexboxlegacy = function() {
            return j("boxDirection")
        }, C.canvas = function() {
            var a = b.createElement("canvas");
            return !(!a.getContext || !a.getContext("2d"))
        }, C.canvastext = function() {
            return !(!o.canvas || !f(b.createElement("canvas").getContext("2d").fillText, "function"))
        }, C.webgl = function() {
            return !!a.WebGLRenderingContext
        }, C.touch = function() {
            var c;
            return "ontouchstart" in a || a.DocumentTouch && b instanceof DocumentTouch ? c = !0 : H(["@media (", x.join("touch-enabled),("), r, ")", "{#modernizr{top:9px;position:absolute}}"].join(""), function(a) {
                c = 9 === a.offsetTop
            }), c
        }, C.geolocation = function() {
            return "geolocation" in navigator
        }, C.postmessage = function() {
            return !!a.postMessage
        }, C.websqldatabase = function() {
            return !!a.openDatabase
        }, C.indexedDB = function() {
            return !!j("indexedDB", a)
        }, C.hashchange = function() {
            return J("hashchange", a) && (b.documentMode === c || b.documentMode > 7)
        }, C.history = function() {
            return !(!a.history || !history.pushState)
        }, C.draganddrop = function() {
            var a = b.createElement("div");
            return "draggable" in a || "ondragstart" in a && "ondrop" in a
        }, C.websockets = function() {
            return "WebSocket" in a || "MozWebSocket" in a
        }, C.rgba = function() {
            return d("background-color:rgba(150,255,150,.5)"), g(t.backgroundColor, "rgba")
        }, C.hsla = function() {
            return d("background-color:hsla(120,40%,100%,.5)"), g(t.backgroundColor, "rgba") || g(t.backgroundColor, "hsla")
        }, C.multiplebgs = function() {
            return d("background:url(https://),url(https://),red url(https://)"), /(url\s*\(.*?){3}/.test(t.background)
        }, C.backgroundsize = function() {
            return j("backgroundSize")
        }, C.borderimage = function() {
            return j("borderImage")
        }, C.borderradius = function() {
            return j("borderRadius")
        }, C.boxshadow = function() {
            return j("boxShadow")
        }, C.textshadow = function() {
            return "" === b.createElement("div").style.textShadow
        }, C.opacity = function() {
            return e("opacity:.55"), /^0.55$/.test(t.opacity)
        }, C.cssanimations = function() {
            return j("animationName")
        }, C.csscolumns = function() {
            return j("columnCount")
        }, C.cssgradients = function() {
            var a = "background-image:",
                b = "gradient(linear,left top,right bottom,from(#9f9),to(white));",
                c = "linear-gradient(left top,#9f9, white);";
            return d((a + "-webkit- ".split(" ").join(b + a) + x.join(c + a)).slice(0, -a.length)), g(t.backgroundImage, "gradient")
        }, C.cssreflections = function() {
            return j("boxReflect")
        }, C.csstransforms = function() {
            return !!j("transform")
        }, C.csstransforms3d = function() {
            var a = !!j("perspective");
            return a && "webkitPerspective" in q.style && H("@media (transform-3d),(-webkit-transform-3d){#modernizr{left:9px;position:absolute;height:3px;}}", function(b) {
                a = 9 === b.offsetLeft && 3 === b.offsetHeight
            }), a
        }, C.csstransitions = function() {
            return j("transition")
        }, C.fontface = function() {
            var a;
            return H('@font-face {font-family:"font";src:url("https://")}', function(c, d) {
                var e = b.getElementById("smodernizr"),
                    f = e.sheet || e.styleSheet,
                    g = f ? f.cssRules && f.cssRules[0] ? f.cssRules[0].cssText : f.cssText || "" : "";
                a = /src/i.test(g) && 0 === g.indexOf(d.split(" ")[0])
            }), a
        }, C.generatedcontent = function() {
            var a;
            return H(["#", r, "{font:0/0 a}#", r, ':after{content:"', v, '";visibility:hidden;font:3px/1 a}'].join(""), function(b) {
                a = b.offsetHeight >= 3
            }), a
        }, C.video = function() {
            var a = b.createElement("video"),
                c = !1;
            try {
                (c = !!a.canPlayType) && (c = new Boolean(c), c.ogg = a.canPlayType('video/ogg; codecs="theora"').replace(/^no$/, ""), c.h264 = a.canPlayType('video/mp4; codecs="avc1.42E01E"').replace(/^no$/, ""), c.webm = a.canPlayType('video/webm; codecs="vp8, vorbis"').replace(/^no$/, ""))
            } catch (d) {}
            return c
        }, C.audio = function() {
            var a = b.createElement("audio"),
                c = !1;
            try {
                (c = !!a.canPlayType) && (c = new Boolean(c), c.ogg = a.canPlayType('audio/ogg; codecs="vorbis"').replace(/^no$/, ""), c.mp3 = a.canPlayType("audio/mpeg;").replace(/^no$/, ""), c.wav = a.canPlayType('audio/wav; codecs="1"').replace(/^no$/, ""), c.m4a = (a.canPlayType("audio/x-m4a;") || a.canPlayType("audio/aac;")).replace(/^no$/, ""))
            } catch (d) {}
            return c
        }, C.localstorage = function() {
            try {
                return localStorage.setItem(r, r), localStorage.removeItem(r), !0
            } catch (a) {
                return !1
            }
        }, C.sessionstorage = function() {
            try {
                return sessionStorage.setItem(r, r), sessionStorage.removeItem(r), !0
            } catch (a) {
                return !1
            }
        }, C.webworkers = function() {
            return !!a.Worker
        }, C.applicationcache = function() {
            return !!a.applicationCache
        }, C.svg = function() {
            return !!b.createElementNS && !!b.createElementNS(B.svg, "svg").createSVGRect
        }, C.inlinesvg = function() {
            var a = b.createElement("div");
            return a.innerHTML = "<svg/>", (a.firstChild && a.firstChild.namespaceURI) == B.svg
        }, C.smil = function() {
            return !!b.createElementNS && /SVGAnimate/.test(w.call(b.createElementNS(B.svg, "animate")))
        }, C.svgclippaths = function() {
            return !!b.createElementNS && /SVGClipPath/.test(w.call(b.createElementNS(B.svg, "clipPath")))
        };
        for (var L in C) m(C, L) && (l = L.toLowerCase(), o[l] = C[L](), F.push((o[l] ? "" : "no-") + l));
        return o.input || k(), o.addTest = function(a, b) {
                if ("object" == typeof a)
                    for (var d in a) m(a, d) && o.addTest(d, a[d]);
                else {
                    if (a = a.toLowerCase(), o[a] !== c) return o;
                    b = "function" == typeof b ? b() : b, "undefined" != typeof p && p && (q.className += " " + (b ? "" : "no-") + a), o[a] = b
                }
                return o
            }, d(""), s = u = null,
            function(a, b) {
                function c(a, b) {
                    var c = a.createElement("p"),
                        d = a.getElementsByTagName("head")[0] || a.documentElement;
                    return c.innerHTML = "x<style>" + b + "</style>", d.insertBefore(c.lastChild, d.firstChild)
                }

                function d() {
                    var a = s.elements;
                    return "string" == typeof a ? a.split(" ") : a
                }

                function e(a) {
                    var b = r[a[p]];
                    return b || (b = {}, q++, a[p] = q, r[q] = b), b
                }

                function f(a, c, d) {
                    if (c || (c = b), k) return c.createElement(a);
                    d || (d = e(c));
                    var f;
                    return f = d.cache[a] ? d.cache[a].cloneNode() : o.test(a) ? (d.cache[a] = d.createElem(a)).cloneNode() : d.createElem(a), !f.canHaveChildren || n.test(a) || f.tagUrn ? f : d.frag.appendChild(f)
                }

                function g(a, c) {
                    if (a || (a = b), k) return a.createDocumentFragment();
                    c = c || e(a);
                    for (var f = c.frag.cloneNode(), g = 0, h = d(), i = h.length; i > g; g++) f.createElement(h[g]);
                    return f
                }

                function h(a, b) {
                    b.cache || (b.cache = {}, b.createElem = a.createElement, b.createFrag = a.createDocumentFragment, b.frag = b.createFrag()), a.createElement = function(c) {
                        return s.shivMethods ? f(c, a, b) : b.createElem(c)
                    }, a.createDocumentFragment = Function("h,f", "return function(){var n=f.cloneNode(),c=n.createElement;h.shivMethods&&(" + d().join().replace(/[\w\-]+/g, function(a) {
                        return b.createElem(a), b.frag.createElement(a), 'c("' + a + '")'
                    }) + ");return n}")(s, b.frag)
                }

                function i(a) {
                    a || (a = b);
                    var d = e(a);
                    return !s.shivCSS || j || d.hasCSS || (d.hasCSS = !!c(a, "article,aside,dialog,figcaption,figure,footer,header,hgroup,main,nav,section{display:block}mark{background:#FF0;color:#000}template{display:none}")), k || h(a, d), a
                }
                var j, k, l = "3.7.0",
                    m = a.html5 || {},
                    n = /^<|^(?:button|map|select|textarea|object|iframe|option|optgroup)$/i,
                    o = /^(?:a|b|code|div|fieldset|h1|h2|h3|h4|h5|h6|i|label|li|ol|p|q|span|strong|style|table|tbody|td|th|tr|ul)$/i,
                    p = "_html5shiv",
                    q = 0,
                    r = {};
                ! function() {
                    try {
                        var a = b.createElement("a");
                        a.innerHTML = "<xyz></xyz>", j = "hidden" in a, k = 1 == a.childNodes.length || function() {
                            b.createElement("a");
                            var a = b.createDocumentFragment();
                            return "undefined" == typeof a.cloneNode || "undefined" == typeof a.createDocumentFragment || "undefined" == typeof a.createElement
                        }()
                    } catch (c) {
                        j = !0, k = !0
                    }
                }();
                var s = {
                    elements: m.elements || "abbr article aside audio bdi canvas data datalist details dialog figcaption figure footer header hgroup main mark meter nav output progress section summary template time video",
                    version: l,
                    shivCSS: m.shivCSS !== !1,
                    supportsUnknownElements: k,
                    shivMethods: m.shivMethods !== !1,
                    type: "default",
                    shivDocument: i,
                    createElement: f,
                    createDocumentFragment: g
                };
                a.html5 = s, i(b)
            }(this, b), o._version = n, o._prefixes = x, o._domPrefixes = A, o._cssomPrefixes = z, o.mq = I, o.hasEvent = J, o.testProp = function(a) {
                return h([a])
            }, o.testAllProps = j, o.testStyles = H, o.prefixed = function(a, b, c) {
                return b ? j(a, b, c) : j(a, "pfx")
            }, q.className = q.className.replace(/(^|\s)no-js(\s|$)/, "$1$2") + (p ? " js " + F.join(" ") : ""), o
    }(this, this.document),
    function() {
        var a = navigator.userAgent.toLowerCase().indexOf("webkit") > -1,
            b = navigator.userAgent.toLowerCase().indexOf("opera") > -1,
            c = navigator.userAgent.toLowerCase().indexOf("msie") > -1;
        if ((a || b || c) && "undefined" != typeof document.getElementById) {
            var d = window.addEventListener ? "addEventListener" : "attachEvent";
            window[d]("hashchange", function() {
                var a = document.getElementById(location.hash.substring(1));
                a && (/^(?:a|select|input|button|textarea)$/i.test(a.tagName) || (a.tabIndex = -1), a.focus())
            }, !1)
        }
    }(),
    function() {
        Array.prototype.indexOf || (Array.prototype.indexOf = function(a) {
            var b = Object(this),
                c = b.length >>> 0;
            if (0 === c) return -1;
            var d = 0;
            if (arguments.length > 0 && (d = Number(arguments[1]), d != d ? d = 0 : 0 != d && 1 / 0 != d && d != -1 / 0 && (d = (d > 0 || -1) * Math.floor(Math.abs(d)))), d >= c) return -1;
            for (var e = d >= 0 ? d : Math.max(c - Math.abs(d), 0); c > e; e++)
                if (e in b && b[e] === a) return e;
            return -1
        });
        var a = ["PointerDown", "PointerUp", "PointerMove", "PointerOver", "PointerOut", "PointerCancel", "PointerEnter", "PointerLeave", "pointerdown", "pointerup", "pointermove", "pointerover", "pointerout", "pointercancel", "pointerenter", "pointerleave"],
            b = "touch",
            c = "pen",
            d = "mouse",
            e = {},
            f = function(a, e) {
                var f;
                if (document.createEvent ? (f = document.createEvent("MouseEvents"), f.initMouseEvent(e, !0, !0, window, 1, a.screenX, a.screenY, a.clientX, a.clientY, a.ctrlKey, a.altKey, a.shiftKey, a.metaKey, a.button, null)) : (f = document.createEventObject(), f.screenX = a.screenX, f.screenY = a.screenY, f.clientX = a.clientX, f.clientY = a.clientY, f.ctrlKey = a.ctrlKey, f.altKey = a.altKey, f.shiftKey = a.shiftKey, f.metaKey = a.metaKey, f.button = a.button), void 0 === f.offsetX && (void 0 !== a.offsetX ? (Object && void 0 !== Object.defineProperty && (Object.defineProperty(f, "offsetX", {
                        writable: !0
                    }), Object.defineProperty(f, "offsetY", {
                        writable: !0
                    })), f.offsetX = a.offsetX, f.offsetY = a.offsetY) : void 0 !== a.layerX && (f.offsetX = a.layerX - a.currentTarget.offsetLeft, f.offsetY = a.layerY - a.currentTarget.offsetTop)), f.isPrimary = void 0 !== a.isPrimary ? a.isPrimary : !0, a.pressure) f.pressure = a.pressure;
                else {
                    var g = 0;
                    void 0 !== a.which ? g = a.which : void 0 !== a.button && (g = a.button), f.pressure = 0 == g ? 0 : .5
                }
                if (f.rotation = a.rotation ? a.rotation : 0, f.hwTimestamp = a.hwTimestamp ? a.hwTimestamp : 0, f.tiltX = a.tiltX ? a.tiltX : 0, f.tiltY = a.tiltY ? a.tiltY : 0, f.height = a.height ? a.height : 0, f.width = a.width ? a.width : 0, f.preventDefault = function() {
                        void 0 !== a.preventDefault && a.preventDefault()
                    }, void 0 !== f.stopPropagation) {
                    var h = f.stopPropagation;
                    f.stopPropagation = function() {
                        void 0 !== a.stopPropagation && a.stopPropagation(), h.call(this)
                    }
                }
                switch (f.POINTER_TYPE_TOUCH = b, f.POINTER_TYPE_PEN = c, f.POINTER_TYPE_MOUSE = d, f.pointerId = a.pointerId, f.pointerType = a.pointerType, f.pointerType) {
                    case 2:
                        f.pointerType = f.POINTER_TYPE_TOUCH;
                        break;
                    case 3:
                        f.pointerType = f.POINTER_TYPE_PEN;
                        break;
                    case 4:
                        f.pointerType = f.POINTER_TYPE_MOUSE
                }
                a.currentTarget && a.currentTarget.handjs_forcePreventDefault === !0 && f.preventDefault(), a.target ? a.target.dispatchEvent(f) : a.srcElement.fireEvent("on" + k(e), f)
            },
            g = function(a, b) {
                a.pointerId = 1, a.pointerType = d, f(a, b)
            },
            h = function(a, c, d, e) {
                var g = c.identifier + 2;
                c.pointerId = g, c.pointerType = b, c.currentTarget = d, c.target = d, void 0 !== e.preventDefault && (c.preventDefault = function() {
                    e.preventDefault()
                }), f(c, a)
            },
            i = function(a, b, c, d) {
                if (c._handjs_registeredEvents)
                    for (var e = 0; e < c._handjs_registeredEvents.length; e++) c._handjs_registeredEvents[e].toLowerCase() === a && h(c._handjs_registeredEvents[e], b, c, d)
            },
            j = function(a, b, c, d) {
                a.preventManipulation && a.preventManipulation();
                for (var f = 0; f < a.changedTouches.length; ++f) {
                    var g = a.changedTouches[f];
                    c && (e[g.identifier] = g.target), d ? i(b, g, e[g.identifier], a) : h(b, g, e[g.identifier], a)
                }
            },
            k = function(a) {
                return a.toLowerCase().replace("pointer", "mouse")
            },
            l = function(b, c, d) {
                var e;
                if (d == d.toLowerCase()) {
                    var f = a.indexOf(d) - a.length / 2;
                    e = c + a[f]
                } else e = c + d;
                return e === c + "PointerEnter" && void 0 === b["on" + c.toLowerCase() + "pointerenter"] && (e = c + "PointerOver"), e === c + "PointerLeave" && void 0 === b["on" + c.toLowerCase() + "pointerleave"] && (e = c + "PointerOut"), e
            },
            m = function(a, b, c, d) {
                d ? a.addEventListener(b, c, !1) : a.removeEventListener(b, c)
            },
            n = function(a, b, c) {
                if (void 0 === a.onpointerdown) {
                    if (void 0 !== a.onmspointerdown) {
                        var d = l(a, "MS", b);
                        return void m(a, d, function(a) {
                            f(a, b)
                        }, c)
                    }
                    if (void 0 !== a.ontouchstart) switch (b.toLowerCase()) {
                        case "pointermove":
                            m(a, "touchmove", function(a) {
                                j(a, b)
                            }, c);
                            break;
                        case "pointercancel":
                            m(a, "touchcancel", function(a) {
                                j(a, b)
                            }, c);
                            break;
                        case "pointerdown":
                        case "pointerup":
                        case "pointerout":
                        case "pointerover":
                        case "pointerleave":
                        case "pointerenter":
                            a._handjs_registeredEvents || (a._handjs_registeredEvents = []);
                            var e = a._handjs_registeredEvents.indexOf(b);
                            c ? -1 === e && a._handjs_registeredEvents.push(b) : a._handjs_registeredEvents.splice(e, 1)
                    }
                    switch (b.toLowerCase()) {
                        case "pointerdown":
                            m(a, "mousedown", function(a) {
                                g(a, b)
                            }, c);
                            break;
                        case "pointermove":
                            m(a, "mousemove", function(a) {
                                g(a, b)
                            }, c);
                            break;
                        case "pointerup":
                            m(a, "mouseup", function(a) {
                                g(a, b)
                            }, c);
                            break;
                        case "pointerover":
                            m(a, "mouseover", function(a) {
                                g(a, b)
                            }, c);
                            break;
                        case "pointerout":
                            m(a, "mouseout", function(a) {
                                g(a, b)
                            }, c);
                            break;
                        case "pointerenter":
                            void 0 === a.onmouseenter ? m(a, "mouseover", function(a) {
                                g(a, b)
                            }, c) : m(a, "mouseenter", function(a) {
                                g(a, b)
                            }, c);
                            break;
                        case "pointerleave":
                            void 0 === a.onmouseleave ? m(a, "mouseout", function(a) {
                                g(a, b)
                            }, c) : m(a, "mouseleave", function(a) {
                                g(a, b)
                            }, c)
                    }
                }
            },
            o = function(b) {
                var c = b.prototype ? b.prototype.addEventListener : b.addEventListener,
                    d = function(b, d, e) {
                        -1 != a.indexOf(b) && n(this, b, !0), void 0 === c ? this.attachEvent("on" + k(b), d) : c.call(this, b, d, e)
                    };
                b.prototype ? b.prototype.addEventListener = d : b.addEventListener = d
            },
            p = function(b) {
                var c = b.prototype ? b.prototype.removeEventListener : b.removeEventListener,
                    d = function(b, d, e) {
                        -1 != a.indexOf(b) && n(this, b, !1), void 0 === c ? this.detachEvent(k(b), d) : c.call(this, b, d, e)
                    };
                b.prototype ? b.prototype.removeEventListener = d : b.removeEventListener = d
            };
        o(document), o(HTMLBodyElement), o(HTMLDivElement), o(HTMLImageElement), o(HTMLUListElement), o(HTMLAnchorElement), o(HTMLLIElement), window.HTMLCanvasElement && o(HTMLCanvasElement), window.SVGElement && o(SVGElement), p(document), p(HTMLBodyElement), p(HTMLDivElement), p(HTMLImageElement), p(HTMLUListElement), p(HTMLAnchorElement), p(HTMLLIElement), window.HTMLCanvasElement && p(HTMLCanvasElement), window.SVGElement && p(SVGElement), void 0 !== window.ontouchstart && (window.addEventListener("touchstart", function(a) {
            for (var b = 0; b < a.changedTouches.length; ++b) {
                var c = a.changedTouches[b];
                e[c.identifier] = c.target, i("pointerenter", c, c.target, a), i("pointerover", c, c.target, a), i("pointerdown", c, c.target, a)
            }
        }), window.addEventListener("touchend", function(a) {
            for (var b = 0; b < a.changedTouches.length; ++b) {
                var c = a.changedTouches[b],
                    d = e[c.identifier];
                i("pointerup", c, d, a), i("pointerout", c, d, a), i("pointerleave", c, d, a)
            }
        }), window.addEventListener("touchmove", function(a) {
            for (var b = 0; b < a.changedTouches.length; ++b) {
                var c = a.changedTouches[b],
                    d = document.elementFromPoint(c.clientX, c.clientY),
                    f = e[c.identifier];
                f !== d && (f && (i("pointerout", c, f, a), f.contains(d) || i("pointerleave", c, f, a)), d && (i("pointerover", c, d, a), d.contains(f) || i("pointerenter", c, d, a)), e[c.identifier] = d)
            }
        })), void 0 === navigator.pointerEnabled && (navigator.pointerEnabled = !0, navigator.msPointerEnabled && (navigator.maxTouchPoints = navigator.msMaxTouchPoints)), document.styleSheets && document.addEventListener && document.addEventListener("DOMContentLoaded", function() {
            var a = function(a) {
                    return a.replace(/^\s+|\s+$/, "")
                },
                b = function(b) {
                    for (var c = new RegExp(".+?{.*?}", "m"), d = new RegExp(".+?{", "m");
                        "" != b;) {
                        var e = c.exec(b)[0];
                        b = a(b.replace(e, ""));
                        var f = a(d.exec(e)[0].replace("{", ""));
                        if (-1 != e.replace(/\s/g, "").indexOf("touch-action:none"))
                            for (var g = document.querySelectorAll(f), h = 0; h < g.length; h++) {
                                var i = g[h];
                                void 0 !== i.style.msTouchAction ? i.style.msTouchAction = "none" : i.handjs_forcePreventDefault = !0
                            }
                    }
                };
            try {
                for (var c = 0; c < document.styleSheets.length; c++) {
                    var d = document.styleSheets[c];
                    if (void 0 != d.href) {
                        var e = new XMLHttpRequest;
                        e.open("get", d.href, !1), e.send();
                        var f = e.responseText.replace(/(\n|\r)/g, "");
                        b(f)
                    }
                }
            } catch (g) {}
            for (var h = document.getElementsByTagName("style"), c = 0; c < h.length; c++) {
                var i = h[c],
                    j = a(i.innerHTML.replace(/(\n|\r)/g, ""));
                b(j)
            }
        }, !1)
    }(), jQuery(function(a) {
        function b() {
            i = window.location.hash.substring(1), console.log("showContentTab newHash=" + i), i && (a("#content").find("#about, #projects,  #news, #tutorials").hide(), a("#content").find("#" + i).show(), a(".project-site-content .current-menu-parent li").each(function() {
                a(this).removeClass("selected");
                var b = (a(this).attr("id"), a(this).children("a")),
                    c = b.attr("title"),
                    d = c.split("-"),
                    e = d[d.length - 1]; - 1 !== i.indexOf(e) && a(this).addClass("selected")
            }))
        }

        function c() {
            i = window.location.hash.substring(1), console.log("showContentTab newHash=" + i), i && (a("#content").find("#about, #projects,  #news, #tutorials").hide(), a("#content").find("#" + i).show(), a(".single-project-nav li").each(function() {
                a(this).removeClass("selected");
                var b = (a(this).attr("id"), a(this).children("a"));
                console.dir(b);
                var c = b.attr("title"),
                    d = c.split("-"),
                    e = d[d.length - 1]; - 1 !== i.indexOf(e) && a(this).addClass("selected")
            }))
        }

        function d() {
            i = window.location.hash.substring(1), console.log("showOsconContentTab newHash=" + i), i && (a("#content").find("#prizes, #labs,  #rules").hide(), a("#content").find("#" + i).show().focus(), a(".oscon-nav li").each(function() {
                a(this).removeClass("selected");
                var b = (a(this).attr("id"), a(this).children("a"));
                console.dir(b);
                var c = b.attr("class"),
                    d = c.split("-"),
                    e = d[d.length - 1]; - 1 !== i.indexOf(e) && a(this).addClass("selected")
            }))
        }

        function e() {
            var b = a(window).width(),
                c = 140;
            600 > b && (c = 60);
            var d = 640;
            if (960 > b) {
                var e = a(".hero-image").innerHeight();
                d = e + 10
            }
            var f = a(window).scrollTop();
            f > c ? a(".navigation-main").addClass("fixed") : a(".navigation-main").removeClass("fixed"), f > d ? a(".oscon-nav").addClass("fixed") : a(".oscon-nav").removeClass("fixed")
        }

        function f() {
            window.scrollTo(0, 1)
        }
        a("#menu-what-we-do li a,  #menu-what-we-do-china li a").addClass("back"), a(".menu, .menu-footer-nav-container").addClass("group"), a(" #menu-what-we-do li, #menu-what-we-do-china li").hover(function(b) {
            a(this).find("div").hoverFlow(b.type, {
                opacity: "hide"
            })
        }, function(b) {
            a(this).find("div").hoverFlow(b.type, {
                opacity: "show"
            })
        }), a('a[title="device-apps-id"], a[title="virtual-machine-depot-id"], a[title="open-web-id"] ').parent().addClass("second-row"), a(' a[title$="-news"], a[title$="-tutorials"] ').parent().addClass("second-row"), a(".project-site-content #about").addClass("hide"), a(".project-site-content #projects").addClass("hide"), a(".project-site-content #news").addClass("hide"), a(".project-site-content #tutorials").addClass("hide"), a(".oscon-site-content #prizes").addClass("hide"), a(".oscon-site-content #labs").addClass("hide"), a(".oscon-site-content #rules").addClass("hide");
        var g = location.hash;
        if ("" == g) a(".project-site-content #about").removeClass("hide"), g = "#about";
        else {
            var h = ".project-site-content " + g;
            a(h).removeClass("hide")
        }
        a(".oscon-content").each(function() {
            console.log("Checking the location hash");
            var b = location.hash;
            if ("" == b) a(".oscon-content #prizes").removeClass("hide"), b = "#prizes";
            else {
                var c = ".oscon-content " + b;
                a(c).removeClass("hide")
            }
            a(".oscon-nav li").each(function() {
                var c = (a(this).attr("id"), a(this).children("a")),
                    d = c.attr("class"),
                    e = d.split("-"),
                    f = e[e.length - 1]; - 1 !== b.indexOf(f) && a(this).addClass("selected")
            })
        }), a(".project-site-content .current-menu-parent li").each(function() {
            var b = (a(this).attr("id"), a(this).children("a")),
                c = b.attr("title"),
                d = c.split("-"),
                e = d[d.length - 1]; - 1 !== g.indexOf(e) && a(this).addClass("selected")
        }), a(".single-project-nav li").each(function() {
            var b = (a(this).attr("id"), a(this).children("a")),
                c = b.attr("title"),
                d = c.split("-"),
                e = d[d.length - 1]; - 1 !== g.indexOf(e) && a(this).addClass("selected")
        }); {
            var i = "";
            a("#content")
        }
        window.onscroll = e, a(window).bind("hashchange", b), a(window).bind("hashchange", c), a(window).bind("hashchange", d), a("#rps .col p.post-title, .window").addClass("group"), a("article header").before('<div class="post-color"></div>'), a("#respond label").after("<br/>");
        a(".blog-sidebar ul li").contents().filter(function() {
            return 3 == this.nodeType
        }).wrap('<span class="catnum">');
        $news = a("#newsSlider");
        var j = a(window).width();
        navigator.pointerEnabled && (jQuery("#mobile-menu").bind("pointerup", function(a) {
            a.preventDefault(), jQuery(".menu-main-nav-menu-container, .menu-main-menu-chn-container").toggle()
        }), 680 >= j && jQuery(".menu-main-nav-menu-container a, .menu-main-menu-chn-container a").bind("pointerup", function() {
            jQuery(".menu-main-nav-menu-container, .menu-main-menu-chn-container").hide()
        })), $news.responsiveSlides({
            maxwidth: 1280,
            speed: 800,
            auto: !0,
            pause: !0,
            nav: !0,
            pager: !0,
            timeout: 5e3,
            before: function() {
                a(".home-news-excerpt").animate({
                    left: "-=40",
                    opacity: 0
                }, 10)
            },
            after: function() {
                a(".home-news-excerpt").animate({
                    left: "+=40",
                    opacity: 1
                }, "400")
            }
        }), a("#newsSlider.myslide").responsiveSlides({
            maxwidth: 1280,
            speed: 800,
            auto: !0,
            pause: !0,
            nav: !0,
            pager: !0,
            timeout: 5e3
        }), addEventListener("load", function() {
            setTimeout(f, 0)
        }, !1), a(".blog-sidebar").scrollToFixed({
            dontSetWidth: !0
        });
        var k = a(".blog-sidebar .baw-year"),
            l = a(".blog-sidebar .baw-month");
        k.hover(function(b) {
            a(this).find(l).hoverFlow(b.type, {
                height: "show",
                marginTop: "show",
                marginBottom: "show",
                paddingTop: "show",
                paddingBottom: "show"
            }, 200)
        }, function(b) {
            a(this).find(l).hoverFlow(b.type, {
                height: "hide",
                marginTop: "hide",
                marginBottom: "hide",
                paddingTop: "hide",
                paddingBottom: "hide"
            }, 200)
        });
        var m = a(".tutorial-downloads h4"),
            n = a(".tut-links"),
            o = a(".tutorial-relationship h4"),
            p = a(".proj-links"),
            q = a(".tutorial-relationship-project h4"),
            r = a(".proj-tut-links");
        m.click(function() {
            n.slideToggle(200)
        }), o.click(function() {
            p.slideToggle(200)
        }), q.click(function() {
            r.slideToggle(200)
        }), console.log("continual work in progress")
    });