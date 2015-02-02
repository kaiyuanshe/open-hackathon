{
    "expr_name": "azure vm test 1",
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
                        "port" : "80",
                        "local_port" : "80"
                    },
                    {
                        "name" : "rdp",
                        "protocol" : "tcp",
                        "port" : "3389",
                        "local_port" : "3389"
                    }
                ]
            },
            "role_size" : "Medium",
            "remote": {
                "provider": "guacamole",
                "protocol": "vnc",
                "input_endpoint_name" : "rdp"
            }
        }
    ]
}