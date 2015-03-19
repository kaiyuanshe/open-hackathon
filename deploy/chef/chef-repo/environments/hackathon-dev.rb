name "hackathon-dev"
description "The open-hackathon development environment"

SSL = {
  :disable => false
}


default_attributes({
  "hackathon" => {
    "debug" => {
      "enable"=> true
    },
    "ssl" => {
      "disableSsl" => SSL[:disable]
    },
    "logging" => {
      "level" => "info"
    }
  }

})
