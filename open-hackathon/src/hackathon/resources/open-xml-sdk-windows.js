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