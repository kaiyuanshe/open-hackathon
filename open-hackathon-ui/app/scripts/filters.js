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
  });

