{
    "name": "windows-server-2016-container-tp4",
    "description" : "Windows Server 2016 Core with Containers Tech Preview 4",
    "virtual_environments": [
        {
            "provider": "1",
            "storage_account" : {
                "service_name" : "opentech0storage",
                "description" : "storage-description",
                "label" : "storage-label",
                "location" : "China East",
                "url_base" : "blob.core.chinacloudapi.cn"
            },
            "container" : "vhds",
            "cloud_service" : {
                "service_name" : "ohp-win2016",
                "label" : "ohp-win2016",
                "location" : "China East"
            },
            "deployment" :{
                "deployment_name" : "ohp-win2016",
                "deployment_slot" : "production"
            },
            "label" : "ohp-win2016",
            "role_name" : "ohp-win2016",
            "image" : {
                "type" : "os",
                "name" : ""
            },
            "system_config" : {
                "os_family" : "Windows",
                "host_name" : "hostname",
                "user_name" : "opentech",
                "user_password" : "Password01!"
            },
            "network_config" : {
                "configuration_set_type" : "NetworkConfiguration",
                "input_endpoints" : [
                    {
                        "name" : "http",
                        "protocol" : "tcp",
                        "local_port" : "80",
                        "url": "http://{0}:{1}"
                    },
                    {
                        "name" : "remote",
                        "protocol" : "tcp",
                        "local_port" : "3389"
                    }
                ]
            },
            "remote": {
                "provider": "guacamole",
                "protocol": "rdp",
                "input_endpoint_name" : "remote"
            },
            "role_size" : "Small"
        }
    ]
}
