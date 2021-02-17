using Kaiyuanshe.OpenHackathon.Server.Biz;
using Microsoft.AspNetCore.Authentication;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using Microsoft.Net.Http.Headers;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.Caching;
using System.Security.Claims;
using System.Text.Encodings.Web;
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

        public DefaultAuthHandler(IOptionsMonitor<DefaultAuthSchemeOptions> options,
            ILoggerFactory logger,
            UrlEncoder encoder, ISystemClock clock,
            IUserManagement userManagement)
            : base(options, logger, encoder, clock)
        {
            this.userManagement = userManagement;
        }
        
        protected override async Task<AuthenticateResult> HandleAuthenticateAsync()
        {
            string failMessage = @"token is required. Please add it to Http Headers: Headers[""Authorization""]=token TOKEN";
            if (!Request.Headers.ContainsKey(HeaderNames.Authorization))
            {
                // No "Authorization" header
                return AuthenticateResult.Fail(failMessage);
            }

            // malformatted
            var authHeader = Request.Headers[HeaderNames.Authorization].LastOrDefault();
            if (!authHeader.StartsWith(TokenPrefix, StringComparison.OrdinalIgnoreCase))
            {
                return AuthenticateResult.Fail(failMessage);
            }

            // validate token existence and expiry
            string token = authHeader.Substring(TokenPrefix.Length);
            string cacheKey = $"token-{DigestHelper.SHA512Digest(token)}";
            var claims = await CacheHelper.GetOrAddAsync(cacheKey,
                () => userManagement.GetCurrentUserClaimsAsync(token),
                new CacheItemPolicy
                {
                    AbsoluteExpiration = DateTime.UtcNow.AddMinutes(10)
                });
            var identity = new ClaimsIdentity(claims, AuthConstant.AuthType.Token);
            var claimsPrincipal = new ClaimsPrincipal(identity);
            return AuthenticateResult.Success(new AuthenticationTicket(claimsPrincipal, AuthConstant.AuthType.Token));
        }
    }
}
