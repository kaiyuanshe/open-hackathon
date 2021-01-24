using Microsoft.AspNetCore.Mvc;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Controllers
{
    public class LoginController : HackathonControllerBase
    {
        public async Task<object> Authing()
        {
            return Ok();
        }
    }
}
