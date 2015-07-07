 {
    "expr_name": "windows",
    "description" : "demo for Windows 10",
    "storage_account" : {
        "service_name" : "hackathon",
        "description" : "storage-description",
        "label" : "storage-label",
        "location" : "China North",
        "url_base" : "blob.core.chinacloudapi.cn"
    },
    "container" : "vhds",
    "cloud_service" : {
        "service_name" : "opentech-win10",
        "label" : "cloud-service-label",
        "location" : "China North"
    },
    "deployment" :{
        "deployment_name" : "opentech-win10",
        "deployment_slot" : "production"
    },
    "virtual_environments": [
        {
            "provider": "azure",
            "label" : "role-label",
            "role_name" : "opentech-win10",
            "system_config" : {
                "os_family" : "Windows",
                "host_name" : "hostname",
                "user_name" : "AzureUser",
                "user_password" : "Password01!"
            },
            "image" : {
                "type" : "os",
                "name" : "win10-161"
            },
            "network_config" : {
                "configuration_set_type" : "NetworkConfiguration",
                "input_endpoints" : [
                    {
                        "name" : "VNC",
                        "protocol" : "tcp",
                        "local_port" : "5900"
                    },
                    {
                        "name" : "Deploy",
                        "protocol" : "tcp",
                        "local_port" : "3389"
                    }
                ]
            },
            "role_size" : "Basic_A3",
            "remote": {
                "provider": "guacamole",
                "protocol": "vnc",
                "username": "CloudUser",
                "password": "acoman",
                "port": 5900,
                "input_endpoint_name" : "Deploy"
            }
        }
    ]
}