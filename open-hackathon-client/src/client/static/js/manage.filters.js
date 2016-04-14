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

angular.module('oh.filters', [])
  .filter('stripTags', function() {
    return function(html) {
      html = html || '';
      return html.replace(/(<([^>]+)>)/ig, '').replace(/&nbsp;/ig, '');
    }
  })
  .filter('split', function() {
    return function(text, limit) {
      limit = limit || ','
      console.log('split');
      if (text) {
        return text.split(limit);
      }
      return [];
    }
  }).filter('defBanner', function() {
    return function(array) {
      return array.length > 0 ? array[0] : '/static/pic/homepage.jpg';
    }
  }).filter('toDate', function() {
    return function(longTime) {
      return new Date(longTime);
    }
  }).filter('isProvider', function() {
    return function(providers, value) {
      providers = parseInt(providers, 10) || 0;
      return value == (providers & value);
    }
  }).filter('inArray', function() {
    return function(array, value) {
      array = array || [];
      return array.indexOf(value) !== -1;
    }
  }).filter('imageStatus',function($translate){
    return function(status){
       switch(status){
        case 0:return $translate.instant('TEMPLATE_STATUS.UNAPPROVED');
        case 1:return $translate.instant('TEMPLATE_STATUS.PASS');
        case 2:return $translate.instant('TEMPLATE_STATUS.FAIL');
       }
       return '';
    }
  }).filter('joinEmails', function() {
    return function(list, filler) {
      filler = filler || ',';
      emailList = []
      if (list) {
        for(var index in list)
          if("email" in list[index])
            emailList.push(list[index].email);
        return emailList.join(filler);
      }
      return '';
    }
  }).filter('hackUserStatus', function($translate){
    return function(status) {
      switch(status) {
        case 0: return $translate.instant('HACK_USER_STATUS.NOAUDIT');
        case 1: return $translate.instant('HACK_USER_STATUS.AUDIT_PASSED');
        case 2: return $translate.instant('HACK_USER_STATUS.AUDIT_REFUSE');
        case 3: return $translate.instant('HACK_USER_STATUS.AUTO_PASSED');
        default: return '';
      }
    }
  }).filter('hackUserType', function($translate){
    return function(type) {
      switch(type) {
        case 0: return $translate.instant('HACK_USER_TYPE.VISITOR');
        case 1: return $translate.instant('HACK_USER_TYPE.ADMIN');
        case 2: return $translate.instant('HACK_USER_TYPE.JUDGE');
        case 3: return $translate.instant('HACK_USER_TYPE.COMPETITOR');
        default: return '';
      }
    }
  }).filter('joinVMs', function() {
    return function(list, filler) {
      filler = filler || ',';
      vmList = []
      if (list) {
        for(var index in list)
          if("name" in list[index])
            vmList.push(list[index].name);
        return vmList.join(filler);
      }
      return '';
    }
  }).filter('exprStatus', function($translate){
    return function(type) {
      switch(type) {
        case 0: return $translate.instant('EXPERIMENT_STATUS.INIT');
        case 1: return $translate.instant('EXPERIMENT_STATUS.STARTING');
        case 2: return $translate.instant('EXPERIMENT_STATUS.RUNNING');
        case 3: return $translate.instant('EXPERIMENT_STATUS.STOPPED');
        case 5: return $translate.instant('EXPERIMENT_STATUS.FAILED');
        case 6: return $translate.instant('EXPERIMENT_STATUS.ROLL_BACKING');
        case 7: return $translate.instant('EXPERIMENT_STATUS.ROLL_BACKED');
        case 8: return $translate.instant('EXPERIMENT_STATUS.UNEXPCTED_ERROR');
        default: return '';
      }
    }
  }).filter('organizationType', function($translate){
    return function(type) {
      switch(parseInt(type)) {
        case 1: return $translate.instant('ORGANIZATION_TYPE.ORGANIZER');
        case 2: return $translate.instant('ORGANIZATION_TYPE.PARTNER');
        default: return '';
      }
    }
  });
