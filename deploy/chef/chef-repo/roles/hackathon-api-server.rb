name "hackathon-api-server"
description "A server that run the API service"

run_list 'recipe[python]',
         'recipe[git]'
