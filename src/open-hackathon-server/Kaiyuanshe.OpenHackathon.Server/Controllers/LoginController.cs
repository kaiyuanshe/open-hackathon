using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.ResponseBuilder;
using Microsoft.AspNetCore.Mvc;
using System;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Controllers
{
    public class LoginController : HackathonControllerBase
    {
        public IUserManagement userManagement { get; set; }

        public IResponseBuilder ResponseBuilder { get; set; }

        /// <summary>
        /// Post the data from Authing after completing the Login process. Open hackathon API
        /// relies on the data for user profile and the token.
        /// </summary>
        /// <param name="parameter"></param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        [HttpPost]
        [Route("login")]
        public async Task<object> Authing([FromBody] UserInfo parameter,
            CancellationToken cancellationToken)
        {
            if (!ModelState.IsValid)
            {
                return BadRequest(ErrorResponse.BadArgument(Resources.Request_Invalid, details: GetErrors()));
            }

            var tokenStatus = await userManagement.ValidateTokenRemotelyAsync(parameter.UserPoolId, parameter.Token, cancellationToken);
            if (!tokenStatus.Status.GetValueOrDefault(false))
            {
                // token invalid
                return BadRequest(ErrorResponse.BadArgument(string.Format(
                    Resources.Auth_Token_ValidateRemoteFailed,
                    tokenStatus.Code.GetValueOrDefault(0),
                    tokenStatus.Message)));
            }


            await userManagement.AuthingAsync(parameter, cancellationToken);
            return Ok(parameter);
        }
    }
}
