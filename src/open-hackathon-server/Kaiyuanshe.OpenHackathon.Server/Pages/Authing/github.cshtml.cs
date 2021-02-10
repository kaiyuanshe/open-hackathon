using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using Newtonsoft.Json.Linq;
using Newtonsoft.Json;
using System.Net.Http;
using System.Text;
using System.Net;
using Authing.ApiClient.Types;

namespace Kaiyuanshe.OpenHackathon.Server.Pages.Authing
{
    public class GithubModel : PageModel
    {
        static readonly HttpClient client = new HttpClient();

        public string Token
        {
            get;
            private set;
        }

        public string UserName
        {
            get;
            private set;
        }

        public async Task OnGet()
        {
            string code = Request.Query["code"];

            if (code != "200")
            {
                // login failed
                return;
            }

            var data = Request.Query["data"];
            User user = JsonConvert.DeserializeObject<User>(data);
            Token = user.Token;
            UserName = user.Name;
        }
    }
}
