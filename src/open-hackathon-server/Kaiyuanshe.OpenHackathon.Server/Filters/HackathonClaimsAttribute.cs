using Kaiyuanshe.OpenHackathon.Server.Authorize;
using Kaiyuanshe.OpenHackathon.Server.Biz;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Filters;
using Microsoft.Net.Http.Headers;
using System;
using System.Linq;
using System.Runtime.Caching;
using System.Security.Claims;

namespace Kaiyuanshe.OpenHackathon.Server.Filters
{
    /// <summary>
    /// Validate 'Authorization' in Http Headers if it's present. The value must be "token YOURTOKEN".
    /// If 'Authorization' is not present or Token is invalid, the <seealso cref="ClaimsPrincipal"/> is anonymous without any <seealso cref="Claim"/>.
    /// </summary>
    [AttributeUsage(AttributeTargets.Class | AttributeTargets.Method, AllowMultiple = false, Inherited = true)]
    public class HackathonClaimsAttribute : TypeFilterAttribute
    {
        public HackathonClaimsAttribute() : base(typeof(HackathonClaimsFilter))
        {

        }

        internal class HackathonClaimsFilter : IActionFilter
        {
            static readonly string TokenPrefix = "token "; // there is a trailling space
            private IUserManagement userManagement;

            public HackathonClaimsFilter(IUserManagement userManagement)
            {
                this.userManagement = userManagement;
            }

            public void OnActionExecuted(ActionExecutedContext context)
            {
            }

            public void OnActionExecuting(ActionExecutingContext context)
            {
                if (!context.HttpContext.Request.Headers.ContainsKey(HeaderNames.Authorization))
                {
                    // No "Authorization" header
                    return;
                }

                // malformatted
                var authHeader = context.HttpContext.Request.Headers[HeaderNames.Authorization].LastOrDefault();
                if (!authHeader.StartsWith(TokenPrefix, StringComparison.OrdinalIgnoreCase))
                {
                    return;
                }

                // validate token existence and expiry
                string token = authHeader.Substring(TokenPrefix.Length);
                string cacheKey = $"token-{DigestHelper.SHA512Digest(token)}";
                var claims = CacheHelper.GetOrAdd(cacheKey,
                    () => userManagement.GetCurrentUserClaimsAsync(token).Result,
                    new CacheItemPolicy
                    {
                        AbsoluteExpiration = DateTime.UtcNow.AddMinutes(10)
                    });
                var identity = new ClaimsIdentity(claims, ClaimConstants.AuthType.Token);
                context.HttpContext.User = new ClaimsPrincipal(identity);
            }
        }
    }
}
