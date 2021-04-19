using Kaiyuanshe.OpenHackathon.Server.Auth;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Routing;
using Microsoft.WindowsAzure.Storage.Table;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Mime;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

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

        #region Frequently used validations

        public class ControllerValiationOptions
        {
            /// <summary>
            /// null if validate successfully. Otherwise a response which desribes the failure
            /// and can be returned to client.
            /// </summary>
            public object ValidateResult { get; set; }

            /// <summary>
            /// optional hackathon name for error message 
            /// </summary>
            public string HackathonName { get; set; } = string.Empty;

            /// <summary>
            /// optional UserId for error message
            /// </summary>
            public string UserId { get; set; } = string.Empty;
        }

        public class ValidateHackathonOptions : ControllerValiationOptions
        {
            public bool EnrollmentOpenRequired { get; set; }
            public bool HackAdminRequird { get; set; }
            public bool OnlineRequired { get; set; }
        }

        public class ValidateEnrollmentOptions : ControllerValiationOptions
        {
            public bool ApprovedRequired { get; set; }
        }

        protected async Task<bool> ValidateHackathon(HackathonEntity hackathon,
            ValidateHackathonOptions options,
            CancellationToken cancellationToken = default)
        {
            options.ValidateResult = null; // make sure it's not set by caller

            if (hackathon == null)
            {
                options.ValidateResult = NotFound(string.Format(Resources.Hackathon_NotFound, options.HackathonName));
                return false;
            }

            if (options.OnlineRequired && hackathon.Status != HackathonStatus.online)
            {
                options.ValidateResult = NotFound(string.Format(Resources.Hackathon_NotFound, options.HackathonName));
                return false;
            }

            if (options.EnrollmentOpenRequired)
            {
                if (hackathon.EnrollmentStartedAt.HasValue && DateTime.UtcNow < hackathon.EnrollmentStartedAt.Value)
                {
                    // enrollment not started
                    options.ValidateResult = PreconditionFailed(string.Format(Resources.Hackathon_Enrollment_NotStarted, hackathon.EnrollmentStartedAt.Value));
                    return false;
                }

                if (hackathon.EnrollmentEndedAt.HasValue && DateTime.UtcNow > hackathon.EnrollmentEndedAt.Value)
                {
                    // enrollment not started
                    options.ValidateResult = PreconditionFailed(string.Format(Resources.Hackathon_Enrollment_Ended, hackathon.EnrollmentEndedAt.Value));
                    return false;
                }
            }

            if (options.HackAdminRequird)
            {
                var authorizationResult = await AuthorizationService.AuthorizeAsync(User, hackathon, AuthConstant.Policy.HackathonAdministrator);
                if (!authorizationResult.Succeeded)
                {
                    options.ValidateResult = Forbidden(Resources.Request_Forbidden_HackAdmin);
                    return false;
                }
            }

            return true;
        }

        protected bool ValidateEnrollment(EnrollmentEntity enrollment, ValidateEnrollmentOptions options)
        {
            if (enrollment == null)
            {
                options.ValidateResult = NotFound(string.Format(Resources.Hackathon_Enrollment_NotFound, options.UserId, options.HackathonName));
                return false;
            }

            if (options.ApprovedRequired && enrollment.Status != EnrollmentStatus.approved)
            {
                options.ValidateResult = PreconditionFailed(Resources.Hackathon_Enrollment_NotApproved);
                return false;
            }

            return true;
        }

        #endregion
    }
}
