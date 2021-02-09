using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.ResponseBuilder;
using Microsoft.AspNetCore.Mvc;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Controllers
{
    public class LoginController : HackathonControllerBase
    {
        public ILoginManager LoginManager { get; set; }

        public IResponseBuilder ResponseBuilder { get; set; }

        [HttpPost]
        [Route("login")]
        public async Task<object> Authing([FromBody] UserLoginInfo parameter,
            CancellationToken cancellationToken)
        {
            if (!ModelState.IsValid)
            {
                return BadRequest(ErrorResponse.BadArgument("Invalid request", details: GetErrors()));
            }

            var tokenStatus = await LoginManager.ValidateAccessTokenAsync(parameter.UserPoolId, parameter.Token, cancellationToken);
            if (!tokenStatus.Status.GetValueOrDefault(false))
            {
                // token invalid
                return BadRequest(ErrorResponse.BadArgument($"Invalid accessToken. Code: {tokenStatus.Code.GetValueOrDefault(0)}, Message: {tokenStatus.Message}"));
            }

            var userEntity = await LoginManager.AuthingAsync(parameter, cancellationToken);
            var tokenEntity = await LoginManager.GetTokenEntityAsync(parameter.Token, cancellationToken);
            return Ok(ResponseBuilder.BuildUserLoginInfo(userEntity, tokenEntity));
        }
    }
}
