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
        public IUserManagement LoginManager { get; set; }

        public IResponseBuilder ResponseBuilder { get; set; }

        /// <summary>
        /// Post the data from Authing after completing the Login process. Open hackathon API
        /// relies on the data for user profile and the token.
        /// </summary>
        /// <param name="parameter"></param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        [HttpPost]
        [Route("authing")]
        public async Task<object> Authing([FromBody] UserInfo parameter,
            CancellationToken cancellationToken)
        {
            if (!ModelState.IsValid)
            {
                return BadRequest(ErrorResponse.BadArgument("Invalid request", details: GetErrors()));
            }

            var tokenStatus = await LoginManager.ValidateTokenRemotelyAsync(parameter.UserPoolId, parameter.Token, cancellationToken);
            if (!tokenStatus.Status.GetValueOrDefault(false))
            {
                // token invalid
                return BadRequest(ErrorResponse.BadArgument($"Invalid accessToken. Code: {tokenStatus.Code.GetValueOrDefault(0)}, Message: {tokenStatus.Message}"));
            }


            await LoginManager.AuthingAsync(parameter, cancellationToken);
            var tokenEntity = await LoginManager.GetTokenEntityAsync(parameter.Token, cancellationToken);
            return Ok(parameter);
        }
    }
}
