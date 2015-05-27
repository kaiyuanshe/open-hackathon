# -----------------------------------------------------------------------------------
# Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# -----------------------------------------------------------------------------------

name "hackathon-docker"
description "Open Hackathon In Docker"


default_attributes({
  "openhackathon" => {
    "admin" => {
      "HOSTNAME" => "http://hackathon.contoso.com",
      "port" => "8000"
    },
    "ui" => {
      "hostname" => "http://hackathon.contoso.com",
      "hackathon_name" => "Sample"
    },
    "environment" => "docker",
    "guacamole" => {
      "host" => "http://hackathon.contoso.com:8080"
    },
    "api" => {
      "endpoint" => "http://hackathon.contoso.com:15000"
    },
    "git" => {
      "repository" => "git@github.com:msopentechcn/open-hackathon.git"
    },
    "github" => {
      "client_id" => "b27959b7639e8b39f873"
    },
    "live" => {
      "client_id" => "0000000040156062"
    },
    "mysql" => {
      "port" => '13312',
      "user_host" => "%",
      "test_data_file_name" => "create_ohid_initial_data.py"
    }
  },
  "java" => {
    "jdk_version" => '7'
  }

})
