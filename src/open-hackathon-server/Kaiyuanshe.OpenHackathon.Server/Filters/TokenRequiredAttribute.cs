using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Filters;
using Microsoft.Net.Http.Headers;
using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Net;
using System.Runtime.CompilerServices;
using System.Threading.Tasks;

[assembly: InternalsVisibleTo("Kaiyuanshe.OpenHackathon.ServerTests")]
namespace Kaiyuanshe.OpenHackathon.Server.Filters
{
    /// <summary>
    /// A valid token must be present in Http Headers: Headers["Authorization"]="token YOURTOKEN"
    /// </summary>
    [AttributeUsage(AttributeTargets.Class | AttributeTargets.Method, AllowMultiple = false, Inherited = true)]
    public class TokenRequiredAttribute : TypeFilterAttribute
    {
        public TokenRequiredAttribute() : base(typeof(TokenRequiredFilter))
        {

        }

        internal class TokenRequiredFilter : IActionFilter
        {
            static readonly string TokenPrefix = "token "; // there is a trailling space
            private ILoginManager loginManager;

            public TokenRequiredFilter(ILoginManager loginManager)
            {
                this.loginManager = loginManager;
            }

            public void OnActionExecuted(ActionExecutedContext context)
            {
            }

            public void OnActionExecuting(ActionExecutingContext context)
            {
                if (!context.HttpContext.Request.Headers.ContainsKey(HeaderNames.Authorization))
                {
                    // No "Authorization" header
                    context.Result = Unauthorized("Header 'Authorization' is missing.");
                    return;
                }

                // malformatted
                var authHeader = context.HttpContext.Request.Headers[HeaderNames.Authorization].LastOrDefault();
                if (!authHeader.StartsWith(TokenPrefix, StringComparison.OrdinalIgnoreCase))
                {
                    context.Result = Unauthorized("Header 'Authorization' is malformatted. Must be of format 'token TOKEN_VALUE'");
                    return;
                }

                // validate token existence and expiry
                string token = authHeader.Substring(TokenPrefix.Length);
                var validationResult = loginManager.ValidateTokenAsync(token).Result;
                if (validationResult != ValidationResult.Success)
                {
                    context.Result = Unauthorized(validationResult.ErrorMessage);
                }
            }

            ObjectResult Unauthorized(string message)
            {
                var error = ErrorResponse.Unauthorized(message);
                return new ObjectResult(error)
                {
                    StatusCode = 401
                };
            }
        }
    }
}
