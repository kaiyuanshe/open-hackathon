using Microsoft.AspNetCore.Mvc;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Kaiyuanshe.OpenHackathon.Server.Models;

namespace Kaiyuanshe.OpenHackathon.Server.Controllers
{
    public class LoginController : HackathonControllerBase
    {
        [HttpPost]
        [Route("login")]
        public async Task<object> Authing([FromBody]UserLoginInfo parameter)
        {
            return Ok(parameter);
        }
    }
}
