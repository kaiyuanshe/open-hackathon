{
    "expr_name": "azure vm test 2",
    "description" : "one storage account, one container, one cloud service, one deployment, multiple virtual machines (Windows/Linux), multiple input endpoints",
    "storage_account" : {
        "service_name" : "yifu0storage",
        "description" : "yifu-test-description",
        "label" : "yifu-test-label",
        "location" : "China East",
        "url_base" : "blob.core.chinacloudapi.cn"
    },
    "container" : "yifu0container",
    "cloud_service" : {
        "service_name" : "yifu-test-service-name",
        "label" : "yifu-test-label",
        "location" : "China East"
    },
    "deployment" :{
        "deployment_name" : "yifu-test-deployment-name",
        "deployment_slot" : "production"
    },
    "virtual_environments": [
        {
            "provider": "azure",
            "label" : "yifu-test-label",
            "role_name" : "yifu-test-role-name",
            "system_config" : {
                "os_family" : "Linux",
                "host_name" : "yifu-test-host-name",
                "user_name" : "yifu-test-user-name",
                "user_password" : "Yifu-Test-User-Password"
            },
            "source_image_name" : "b549f4301d0b4295b8e76ceb65df47d4__Ubuntu-14_04_1-LTS-amd64-server-20141125-en-us-30GB",
            "network_config" : {
                "configuration_set_type" : "NetworkConfiguration",
                "input_endpoints" : [
                    {
                        "name" : "ssh",
                        "protocol" : "tcp",
                        "port" : "122",
                        "local_port" : "22"
                    },
                    {
                        "name" : "http",
                        "protocol" : "tcp",
                        "port" : "180",
                        "local_port" : "80"
                    }
                ]
            },
            "role_size" : "Small"
        },
        {
            "provider": "azure",
            "label" : "yifu-test-label-2",
            "role_name" : "yifu-test-role-name-2",
            "system_config" : {
                "os_family" : "Windows",
                "host_name" : "yifutest2",
                "user_name" : "yifutestuser2",
                "user_password" : "Yifu-Test--2"
            },
            "source_image_name" : "0c5c79005aae478e8883bf950a861ce0__Windows-Server-2012-Essentials-20141204-enus",
            "network_config" : {
                "configuration_set_type" : "NetworkConfiguration",
                "input_endpoints" : [
                    {
                        "name" : "http",
                        "protocol" : "tcp",
                        "port" : "181",
                        "local_port" : "80"
                    }
                ]
            },
            "role_size" : "Small"
        }
    ]
}