﻿using Kaiyuanshe.OpenHackathon.Server.Biz;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Filters;
using Microsoft.Net.Http.Headers;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Security.Claims;
using System.Threading.Tasks;

[assembly: InternalsVisibleTo("Kaiyuanshe.OpenHackathon.ServerTests")]
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
            private IUserManagement loginManager;

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
                //var validationResult = loginManager.ValidateTokenAsync(token).Result;
                //if (validationResult != ValidationResult.Success)
                //{
                //    context.Result = Unauthorized(validationResult.ErrorMessage);
                //}
            }
        }
    }
}
