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

name "hackathon-dev"
description "The open-hackathon development environment"


default_attributes({
  "openhackathon" => {
    "environment" => "dev",
    "guacamole" => {
      "host" => "http://open-hackathon.chinacloudapp.cn:28080"
    },
    "api" => {
      "endpoint" => "http://open-hackathon-dev.chinacloudapp.cn:15000"
    },
    "git" => {
      "repository" => "git@github.com:msopentechcn/open-hackathon.git"
    },
    "gitcafe" => {
      "api_domain" => "https://gcas.dgz.sh",
      "client_id" => "1c33ecdf4dd0826325f60a92e91834522b1cdf47a7f90bdaa79f0526fdc48727",
      "client_secret" => "80b63609000b20c1260df28081c08712617648e1b528086bbb089f0af4614509",
      "domain" => "https://gcs.dgz.sh"
    },
    "qq" => {
      "client_id" => "101200890",
      "client_secret" => "88ad67bd4521c4cc47136854781cb9b5",
      "meta_content" => "274307566465013314076545663016134754100636"
    },
    "weibo" => {
      "client_id" => "1943560862",
      "client_secret" => "a5332c39c129902e561bff5e4bcc5982"
    },
    "github" => {
      "client_id" => "b8e407813350f26bf537",
      "client_secret" => "daa78ae27e13c9f5b4a884bd774cadf2f75a199f"
    },
    "mysql" => {
      "port" => '13312',
      "user_host" => "%"
    }
  }

})

