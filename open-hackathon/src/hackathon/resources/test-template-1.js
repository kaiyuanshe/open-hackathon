{
    "expr_name": "test template 1",
    "description" : "a template consists of a list of virtual environments, and a virtual environment is a virtual machine with its storage account, container, cloud service and deployment",
    "virtual_environments": [
        {
            "provider": "azure",
            "storage_account" : {
                "service_name" : "portalvhdsnc364fhj0dlpp",
                "description" : "storage-description",
                "label" : "storage-label",
                "location" : "China East",
                "url_base" : "blob.core.chinacloudapi.cn"
            },
            "container" : "vhds",
            "cloud_service" : {
                "service_name" : "ot-service-test",
                "label" : "cloud-service-label",
                "location" : "China East"
            },
            "deployment" :{
                "deployment_name" : "ot-deployment-test",
                "deployment_slot" : "production"
            },
            "label" : "role-label",
            "role_name" : "ot-role-test",
            "image" : {
                "type" : "vm",
                "name" : "openxml"
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
                        "local_port" : "80"
                    },
                    {
                        "name" : "Deploy",
                        "protocol" : "tcp",
                        "local_port" : "3389"
                    }
                ]
            },
            "remote": {
                "provider": "guacamole",
                "protocol": "rdp",
                "input_endpoint_name" : "Deploy"
            },
            "role_size" : "Small"
        }
    ]
}