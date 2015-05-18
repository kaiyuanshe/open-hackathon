name "hackathon-docker"
description "The open-hackathon dockerized environment"


default_attributes({
  "openhackathon" => {
    "admin" => {
      "HOSTNAME" => "http://admin.contoso.com",
      "port" => "8000"
    }
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
      "user_host" => "%"
    }
  }

})
