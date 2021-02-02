using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;

namespace Kaiyuanshe.OpenHackathon.Server.Pages.Authing
{
    public class GithubModel : PageModel
    {
        public string Token 
        { 
            get; 
            private set;
        }

        public void OnGet()
        {
            string code = Request.Query["code"];

            if(code != "200")
            {
                // login failed
                return;
            }

            Token = "Testing";
        }
    }
}
