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

{
    "expr_name": "windows",
    "description" : "one storage account, one container, one cloud service, one deployment, multiple virtual machines (Windows/Linux), multiple input endpoints",
    "storage_account" : {
        "service_name" : "portalvhdsnc364fhj0dlpp",
        "description" : "storage-description",
        "label" : "storage-label",
        "location" : "China East",
        "url_base" : "blob.core.chinacloudapi.cn"
    },
    "container" : "vhds",
    "cloud_service" : {
        "service_name" : "open-tech-service",
        "label" : "cloud-service-label",
        "location" : "China East"
    },
    "deployment" :{
        "deployment_name" : "open-tech-deployment",
        "deployment_slot" : "production"
    },
    "virtual_environments": [
        {
            "provider": "azure",
            "label" : "role-label",
            "role_name" : "open-tech-role-test",
            "system_config" : {
                "os_family" : "Windows",
                "host_name" : "hostname",
                "user_name" : "azureUser888",
                "user_password" : "PASSword00X"
            },
            "image" : {
                "type" : "vm",
                "name" : "openxml"
            },
            "network_config" : {
                "configuration_set_type" : "NetworkConfiguration",
                "input_endpoints" : [
                    {
                        "name" : "http",
                        "protocol" : "tcp",
                        "port" : "80",
                        "local_port" : "80"
                    },
                    {
                        "name" : "Deploy",
                        "protocol" : "tcp",
                        "port" : "3389",
                        "local_port" : "3389"
                    }
                ]
            },
            "role_size" : "Basic_A3",
            "remote": {
                "provider": "guacamole",
                "protocol": "rdp",
                "input_endpoint_name" : "Deploy"
            }
        }
    ]
}