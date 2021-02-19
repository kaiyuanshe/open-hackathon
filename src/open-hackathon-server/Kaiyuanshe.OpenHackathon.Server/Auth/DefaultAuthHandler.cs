using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using Microsoft.Net.Http.Headers;
using Newtonsoft.Json;
using System;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Net;
using System.Net.Mime;
using System.Security.Claims;
using System.Text.Encodings.Web;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Auth
{
    public class DefaultAuthSchemeOptions : AuthenticationSchemeOptions
    {

    }

    /// <summary>
    /// A empty implementation of AuthenticationHandler to make dotnet core happy.
    /// </summary>
    public class DefaultAuthHandler : AuthenticationHandler<DefaultAuthSchemeOptions>
    {
        static readonly string TokenPrefix = "token "; // there is a trailling space
        private IUserManagement userManagement;
        private Func<HttpResponse, string, CancellationToken, Task> writeToResponse;

        public DefaultAuthHandler(IOptionsMonitor<DefaultAuthSchemeOptions> options,
            ILoggerFactory logger,
            UrlEncoder encoder, ISystemClock clock,
            IUserManagement userManagement,
            Func<HttpResponse, string, CancellationToken, Task> writeToResponse = null)
            : base(options, logger, encoder, clock)
        {
            this.userManagement = userManagement;
            this.writeToResponse = writeToResponse ?? HttpResponseWritingExtensions.WriteAsync;
        }

        protected override async Task<AuthenticateResult> HandleAuthenticateAsync()
        {
            if (!Request.Headers.ContainsKey(HeaderNames.Authorization))
            {
                // No "Authorization" header
                return AuthenticateResult.Fail(Resources.Auth_Unauthorized);
            }

            // malformatted
            var authHeader = Request.Headers[HeaderNames.Authorization].LastOrDefault();
            if (!authHeader.StartsWith(TokenPrefix, StringComparison.OrdinalIgnoreCase))
            {
                return AuthenticateResult.Fail(Resources.Auth_Unauthorized);
            }

            // validate token existence and expiry
            string token = authHeader.Substring(TokenPrefix.Length);
            var validationResult = await userManagement.ValidateTokenAsync(token);
            if (validationResult != ValidationResult.Success)
            {
                return AuthenticateResult.Fail(Resources.Auth_Unauthorized);
            }

            // get Claims
            string cacheKey = CacheKey.Get(CacheKey.Section.Token, DigestHelper.SHA512Digest(token));
            var claims = await CacheHelper.GetOrAddAsync(cacheKey,
                () => userManagement.GetUserBasicClaimsAsync(token),
                CacheHelper.ExpireIn10M);
            var identity = new ClaimsIdentity(claims, AuthConstant.AuthType.Token);
            var claimsPrincipal = new ClaimsPrincipal(identity);
            return AuthenticateResult.Success(new AuthenticationTicket(claimsPrincipal, AuthConstant.AuthType.Token));
        }

        protected override async Task HandleChallengeAsync(AuthenticationProperties properties)
        {
            Response.StatusCode = (int)HttpStatusCode.Unauthorized;
            Response.ContentType = MediaTypeNames.Application.Json;
            await writeToResponse(Response, JsonConvert.SerializeObject(ErrorResponse.Unauthorized(Resources.Auth_Unauthorized)), CancellationToken.None);
        }

        protected override async Task HandleForbiddenAsync(AuthenticationProperties properties)
        {
            Response.StatusCode = (int)HttpStatusCode.Forbidden;
            Response.ContentType = MediaTypeNames.Application.Json;
            await writeToResponse(Response, JsonConvert.SerializeObject(ErrorResponse.Forbidden(Resources.Auth_Forbidden)), CancellationToken.None);
        }
    }
}
