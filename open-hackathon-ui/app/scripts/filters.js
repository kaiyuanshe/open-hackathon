/*
 * Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
 *
 * The MIT License (MIT)
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

'use strict';

/**
 * Created by v-boguan on 2015/5/4.
 */

angular.module('oh.app')
  .filter('mkHTML', function () {
    return function (text) {
      return markdown.toHTML(text || '');
    }
  })
  .filter('stripTags', function () {
    return function (html) {
      html = html || '';
      return html.replace(/(<([^>]+)>)/ig, '');
    }
  })
  .filter('split', function () {
    return function (text, limit) {
      limit = limit || ',';
      text = text || '';
      return text.split(limit);
    }
  })
  .filter('defBanner', function () {
    return function (array) {
      return array[0].length > 0 ? array[0] : '/images/homepage.jpg';
    }
  }).filter('toDate', function () {
    return function (longTime) {
      return new Date(longTime);
    }
  }).filter('skypelink', function () {
    return function (skype) {
      return skype.length > 0 ? 'skype:' + skype + '?chat' : 'javascript:;';
    }
  }).filter('timeago', function ($filter) {
    return function (time, local, raw) {
      if (!local) {
        (local = Date.now())
      }

      if (angular.isDate(local)) {
        local = local.getTime();
      } else if (typeof local === "string") {
        local = new Date(local).getTime();
      }
      var offset = Math.abs((local - time) / 1000),
        span = '',
        MINUTE = 60,
        HOUR = 3600,
        DAY = 86400;
      if (offset <= MINUTE) {
        span = '刚刚';
      } else if (offset < (MINUTE * 60)) {
        span = Math.round(Math.abs(offset / MINUTE)) + '分钟前';
      } else if (offset < (HOUR * 24)) {
        span = Math.round(Math.abs(offset / HOUR)) + '小时前';
      } else if (offset < (DAY * 1)) {
        span = '昨天'
      } else if (offset < (DAY * 3)) {
        span = Math.round(Math.abs(offset / DAY)) + '天之前';
      } else {
        span = $filter('data')(time, '')
      }
      return span;
    }
  });

