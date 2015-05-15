name "hackathon-docker"
description "The open-hackathon dockerized environment"


default_attributes({
  "openhackathon" => {
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
    "gitcafe" => {
      "api_domain" => "",
      "client_id" => "",
      "client_secret" => "",
      "domain" => ""
    },
    "qq" => {
      "client_id" => "",
      "client_secret" => "",
      "meta_content" => ""
    },
    "weibo" => {
      "client_id" => "",
      "client_secret" => ""
    },
    "github" => {
      "client_id" => "b27959b7639e8b39f873",
      "client_secret" => "a727029295d9e871a1e55dda75c8fb6bf1ed0d4c"
    },
    "live" => {
      "client_id" => "0000000040156062",
      "client_secret" => "X3ZuhIuR7QI-xZAcxGn041vo0r13eN73"
    },
    "mysql" => {
      "port" => '13312',
      "user_host" => "%"
    }
  }

})