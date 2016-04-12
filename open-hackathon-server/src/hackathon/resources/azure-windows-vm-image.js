{
    "name": "azure-windows-vm-image",
    "description" : "use azure vm image to create a windows virtual machine",
    "virtual_environments": [
        {
            "provider": "1",
            "storage_account" : {
                "service_name" : "rapidtest",
                "description" : "storage-description",
                "label" : "storage-label",
                "location" : "China East",
                "url_base" : "blob.core.chinacloudapi.cn"
            },
            "container" : "vhds",
            "cloud_service" : {
                "service_name" : "rapid-test",
                "label" : "cloud-service-label",
                "location" : "China East"
            },
            "deployment" :{
                "deployment_name" : "rapid-test-deployment",
                "deployment_slot" : "production"
            },
            "label" : "rapid-test",
            "role_name" : "rapid-test",
            "image" : {
                "type" : "vm",
                "name" : "rapid-test-25-20160111-203213"
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
