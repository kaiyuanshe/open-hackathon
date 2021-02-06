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

            if(code != "200")
            {
                // login failed
                return;
            }

            var data = Request.Query["data"];
            
            var loginUrl = $"{Request.Scheme}://{Request.Host}/v2/login";
            if(Request.Host.Host == "localhost")
            {
                loginUrl = $"http://localhost:5000/v2/login";
            }
            var content = new StringContent(data, Encoding.UTF8, "application/json");
            HttpResponseMessage response = await client.PostAsync(loginUrl, content);
            string responseBody = await response.Content.ReadAsStringAsync();
            Console.WriteLine(responseBody);
            if(response.IsSuccessStatusCode)
            {
                var jsonObject = JObject.Parse(responseBody);
                UserName = jsonObject.Value<string>("userName");

                // read token from data. oph login api don't return token
                var user = JsonConvert.DeserializeObject<Models.UserLoginInfo>(data);
                Token = user.Token;
            }
            else
            {
                Console.WriteLine($"code: {response.StatusCode}");
                Console.WriteLine($"body: {responseBody}");
            }
        }
    }
}
