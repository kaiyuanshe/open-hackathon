using Kaiyuanshe.OpenHackathon.Server.Auth;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Mime;

namespace Kaiyuanshe.OpenHackathon.Server.Controllers
{
    [ApiController]
    [Consumes(MediaTypeNames.Application.Json)]
    [Produces(MediaTypeNames.Application.Json)]
    [Route("v2")]
    public abstract class HackathonControllerBase : ControllerBase
    {
        public IAuthorizationService AuthorizationService { get; set; }

        /// <summary>
        /// Id of current User. Return string.Empty if token is not required or invalid.
        /// </summary>
        protected string CurrentUserId
        {
            get
            {
                var userIdClaim = User?.Claims?.FirstOrDefault(c => c.Type == AuthConstant.ClaimType.UserId);
                return userIdClaim?.Value ?? string.Empty;
            }
        }

        #region ObjectResult with ProblemDetails
        protected ObjectResult BadRequest(string detail, string instance = null)
        {
            return Problem(
                statusCode: 400,
                detail: detail,
                instance: instance);
        }

        protected ObjectResult Unauthorized(string detail, string instance = null)
        {
            return Problem(
                statusCode: 401,
                detail: detail,
                instance: instance);
        }

        protected ObjectResult Forbidden(string detail, string instance = null)
        {
            return Problem(
                statusCode: 403,
                detail: detail,
                instance: instance);
        }

        protected ObjectResult NotFound(string detail, string instance = null)
        {
            return Problem(
                statusCode: 404,
                detail: detail,
                instance: instance);
        }

        protected ObjectResult Conflict(string detail, string instance = null)
        {
            return Problem(
                statusCode: 409,
                detail: detail,
                instance: instance);
        }
        #endregion
    }
}
