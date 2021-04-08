using Kaiyuanshe.OpenHackathon.Server.Auth;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Routing;
using Microsoft.WindowsAzure.Storage.Table;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Mime;
using System.Text;

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
                return ClaimsHelper.GetUserId(User);
            }
        }

        /// <summary>
        /// Get nextLink url for paginated results
        /// </summary>
        /// <param name="routeValues">values to generate url. Values of current url are implicitly used. 
        /// Add extra key/value pairs or modifications to routeValues. Values not used in route will be appended as QueryString.</param>
        /// <returns></returns>
        protected string BuildNextLinkUrl(RouteValueDictionary routeValues, TableContinuationToken continuationToken)
        {
            if (continuationToken == null)
                return null;

            if (routeValues == null)
            {
                routeValues = new RouteValueDictionary();
            }
            routeValues.Add(nameof(Pagination.np), continuationToken.NextPartitionKey);
            routeValues.Add(nameof(Pagination.nr), continuationToken.NextRowKey);

            if (EnvHelper.IsRunningInTests())
            {
                // Unit Test
                StringBuilder stringBuilder = new StringBuilder();
                foreach (var key in routeValues.Keys)
                {
                    stringBuilder.Append($"&{key}={routeValues[key]}");
                }
                return stringBuilder.ToString();
            }

            return Url.Action(
               ControllerContext.ActionDescriptor.ActionName,
               ControllerContext.ActionDescriptor.ControllerName,
               routeValues,
               Request.Scheme,
               Request.Host.Value);
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

        protected ObjectResult PreconditionFailed(string detail, string instance = null)
        {
            return Problem(
                statusCode: 412,
                detail: detail,
                instance: instance
            );
        }
        #endregion
    }
}
