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

angular.module('oh.pages', [])
  .constant('VERSION', '0.2.0')
  .value('NAV', {
    manage: [{
      name: "SETTINGS.MAIN",
      type: 1,
      navGroups: [{
        name: "SETTINGS.EDIT_ACTIVITY",
        state: "manage.edit",
        icon: 'fa-edit'
      }, {
        name: "SETTINGS.USERS",
        state: "manage.users",
        icon: 'fa-user'
      }, {
        name: "SETTINGS.ADMINISTRATORS",
        state: "manage.admin",
        icon: 'fa-user-secret'
      }, {
        name: "SETTINGS.ORGANIZERS",
        state: "manage.organizers",
        icon: 'fa-sitemap'
      }, {
        name: "SETTINGS.PRIZES",
        state: "manage.prizes",
        icon: 'fa-trophy'
      }, {
        name: "SETTINGS.AWARDS",
        state: "manage.awards",
        icon: 'fa-diamond'
      }, {
        name: "SETTINGS.NOTICES",
        state: "manage.notices",
        icon: 'fa-bullhorn'
      }]
    }, {
      name: "ADVANCED_SETTINGS.MAIN",
      type: 2,
      navGroups: [{
        name: "ADVANCED_SETTINGS.CLOUD_RESOURCES",
        state: "manage.cloud",
        icon: 'fa-upload'
      }, {
        name: "ADVANCED_SETTINGS.VIRTUAL_ENVIRONMENT",
        state: "manage.ve",
        icon: 'fa-th-large'
      }, {
        name: "ADVANCED_SETTINGS.ENVIRONMENTAL_MONITOR",
        state: "manage.monitor",
        icon: 'fa-desktop'
      }, {
        name: "ADVANCED_SETTINGS.AZURECERT",
        state: "manage.azurecert",
        icon: 'fa-cloud-upload'
      }, {
        name: "ADVANCED_SETTINGS.SERVERS",
        state: "manage.servers",
        icon: 'fa-server'
      }]
    }]
  });
