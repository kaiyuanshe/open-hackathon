   var clientId = '304944766846-7jt8jbm39f1sj4kf4gtsqspsvtogdmem.apps.googleusercontent.com';

var apiKey = 'AIzaSyAnLbBT3Hy2PfSEUoLwsjbgqSm5H3cHQfk';

var scopes = 'https://www.googleapis.com/auth/plus.me';

 function handleClientLoad() {
        gapi.client.setApiKey(apiKey);
       // window.setTimeout(checkAuth,1);
      }

      function checkAuth() {
        gapi.auth.authorize({client_id: clientId, scope: scopes, immediate: true}, handleAuthResult);
      }


      function handleAuthResult(authResult) {
     //   var authorizeButton = document.getElementById('googlelogin');
        if (authResult && !authResult.error) {
         // authorizeButton.style.visibility = 'hidden';
          makeApiCall();
        } else {
          //authorizeButton.style.visibility = '';
          authorizeButton.onclick = handleAuthClick;
        }
      }

      function handleAuthClick(event) {
        gapi.auth.authorize({client_id: clientId, scope: scopes, immediate: false}, handleAuthResult);
        return false;
      }

      // Load the API and make an API call.  Display the results on the screen.
      function makeApiCall() {
        gapi.client.load('plus', 'v1', function() {
          var request = gapi.client.plus.people.get({
            'userId': 'me'
          });
          request.execute(function(resp) {
            var heading = document.createElement('h4');
            var image = document.createElement('img');
            image.src = "https://lh3.googleusercontent.com/-XdUIqdMkCWA/AAAAAAAAAAI/AAAAAAAAAAA/4252rscbv5M/photo.jpg?sz=50";
            heading.appendChild(image);
            heading.appendChild(document.createTextNode(resp.displayName));

            document.getElementById('contentxx').appendChild(heading);
          });
        });
      }

        $(function() {
                var authorizeButton =  document.getElementById('googlelogin');
                authorizeButton.onclick = handleAuthClick;
        })

