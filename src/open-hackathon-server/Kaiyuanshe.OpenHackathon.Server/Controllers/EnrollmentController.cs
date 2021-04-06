using Kaiyuanshe.OpenHackathon.Server.Auth;
using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.ResponseBuilder;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Kaiyuanshe.OpenHackathon.Server.Swagger;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Routing;
using System;
using System.ComponentModel.DataAnnotations;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Controllers
{
    public class EnrollmentController : HackathonControllerBase
    {
        public IResponseBuilder ResponseBuilder { get; set; }

        public IHackathonManagement HackathonManagement { get; set; }

        /// <summary>
        /// Enroll a hackathon.
        /// </summary>
        /// <param name="parameter"></param>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <returns>The enrollment</returns>
        /// <response code="200">Success. The response describes a enrollment.</response>
        [HttpPost]
        [ProducesResponseType(typeof(Enrollment), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 404, 412)]
        [Route("hackathon/{hackathonName}/enrollment")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.LoginUser)]
        public async Task<object> Enroll(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromBody] Enrollment parameter)
        {
            HackathonEntity hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackathonName.ToLower());
            if (hackathon == null)
            {
                return NotFound(string.Format(Resources.Hackathon_NotFound, hackathonName.ToLower()));
            }

            if (hackathon.EnrollmentStartedAt.HasValue && DateTime.UtcNow < hackathon.EnrollmentStartedAt.Value)
            {
                // enrollment not started
                return PreconditionFailed(string.Format(Resources.Hackathon_Enrollment_NotStarted, hackathon.EnrollmentStartedAt.Value));
            }

            if (hackathon.EnrollmentEndedAt.HasValue && DateTime.UtcNow > hackathon.EnrollmentEndedAt.Value)
            {
                // enrollment not started
                return PreconditionFailed(string.Format(Resources.Hackathon_Enrollment_Ended, hackathon.EnrollmentEndedAt.Value));
            }

            var participant = await HackathonManagement.EnrollAsync(hackathon, CurrentUserId);
            return Ok(ResponseBuilder.BuildEnrollment(participant));
        }


        /// <summary>
        /// Get a hackathon enrollement for current user.
        /// </summary>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <returns>The enrollment</returns>
        /// <response code="200">Success.</response>
        [HttpGet]
        [ProducesResponseType(typeof(Enrollment), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 404)]
        [Route("hackathon/{hackathonName}/enrollment")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.LoginUser)]
        public async Task<object> Get([FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName)
        {
            var enrollment = await HackathonManagement.GetEnrollmentAsync(hackathonName.ToLower(), CurrentUserId);
            if (enrollment == null)
            {
                return NotFound(string.Format(Resources.Hackathon_Enrollment_NotFound, CurrentUserId, hackathonName));
            }

            return Ok(ResponseBuilder.BuildEnrollment(enrollment));
        }

        /// <summary>
        /// Approve a hackathon enrollement.
        /// </summary>
        /// <param name="parameter"></param>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="userId" example="1">Id of user</param>
        /// <returns>The enrollment</returns>
        /// <response code="200">Success. The enrollment is approved.</response>
        [HttpPost]
        [ProducesResponseType(typeof(Enrollment), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 403, 404)]
        [Route("hackathon/{hackathonName}/enrollment/{userId}/approve")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.HackathonAdministrator)]
        public async Task<object> Approve(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required] string userId,
            [FromBody] Enrollment parameter)
        {
            return await UpdateEnrollmentStatus(hackathonName.ToLower(), userId.ToLower(), EnrollmentStatus.approved);
        }

        /// <summary>
        /// Reject a hackathon enrollement.
        /// </summary>
        /// <param name="parameter"></param>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="userId" example="1">Id of user</param>
        /// <returns>The enrollment</returns>
        /// <response code="200">Success. The enrollment is approved.</response>
        [HttpPost]
        [ProducesResponseType(typeof(Enrollment), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 403, 404)]
        [Route("hackathon/{hackathonName}/enrollment/{userId}/reject")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.HackathonAdministrator)]
        public async Task<object> Reject(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required] string userId,
            [FromBody] Enrollment parameter)
        {
            return await UpdateEnrollmentStatus(hackathonName.ToLower(), userId.ToLower(), EnrollmentStatus.rejected);
        }

        private async Task<object> UpdateEnrollmentStatus(string hackathonName, string userId, EnrollmentStatus status)
        {
            HackathonEntity hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackathonName);
            if (hackathon == null)
            {
                return NotFound(string.Format(Resources.Hackathon_NotFound, hackathonName));
            }

            var authorizationResult = await AuthorizationService.AuthorizeAsync(User, hackathon, AuthConstant.Policy.HackathonAdministrator);
            if (!authorizationResult.Succeeded)
            {
                return Forbidden(Resources.Request_Forbidden_HackAdmin);
            }

            EnrollmentEntity enrollment = await HackathonManagement.GetEnrollmentAsync(hackathonName, userId);
            if (enrollment == null)
            {
                return NotFound(string.Format(Resources.Hackathon_Enrollment_NotFound, userId, hackathonName));
            }

            enrollment = await HackathonManagement.UpdateEnrollmentStatusAsync(enrollment, status);
            return Ok(ResponseBuilder.BuildEnrollment(enrollment));
        }

        /// <summary>
        /// Get a hackathon enrollement of any enrolled user. Hackthon admin only.
        /// </summary>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="userId" example="1">Id of user</param>
        /// <returns>The enrollment</returns>
        /// <response code="200">Success.</response>
        [HttpGet]
        [ProducesResponseType(typeof(Enrollment), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 403, 404)]
        [Route("hackathon/{hackathonName}/enrollment/{userId}")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.HackathonAdministrator)]
        public async Task<object> GetByAdmin(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required] string userId)
        {
            var hackName = hackathonName.ToLower();
            HackathonEntity hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackName);
            if (hackathon == null)
            {
                return NotFound(string.Format(Resources.Hackathon_NotFound, hackathonName));
            }

            var authorizationResult = await AuthorizationService.AuthorizeAsync(User, hackathon, AuthConstant.Policy.HackathonAdministrator);
            if (!authorizationResult.Succeeded)
            {
                return Forbidden(Resources.Request_Forbidden_HackAdmin);
            }

            EnrollmentEntity enrollment = await HackathonManagement.GetEnrollmentAsync(hackName, userId.ToLower());
            if (enrollment == null)
            {
                return NotFound(string.Format(Resources.Hackathon_Enrollment_NotFound, userId, hackathonName));
            }
            return Ok(ResponseBuilder.BuildEnrollment(enrollment));
        }

        /// <summary>
        /// List paginated enrollements of a hackathon.
        /// </summary>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="status" example="approved">filter by enrollment status</param>
        /// <returns>the response contains a list of enrollments and a nextLink if there are more results.</returns>
        /// <response code="200">Success.</response>
        [HttpGet]
        [ProducesResponseType(typeof(EnrollmentList), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 403)]
        [Route("hackathon/{hackathonName}/enrollments")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.HackathonAdministrator)]
        public async Task<object> ListEnrollments(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromQuery] Pagination pagination,
            [FromQuery] EnrollmentStatus? status,
            CancellationToken cancellationToken)
        {
            var hackName = hackathonName.ToLower();
            HackathonEntity hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackName);
            if (hackathon == null)
            {
                return NotFound(string.Format(Resources.Hackathon_NotFound, hackathonName));
            }

            var authorizationResult = await AuthorizationService.AuthorizeAsync(User, hackathon, AuthConstant.Policy.HackathonAdministrator);
            if (!authorizationResult.Succeeded)
            {
                return Forbidden(Resources.Request_Forbidden_HackAdmin);
            }

            var options = new EnrollmentQueryOptions
            {
                TableContinuationToken = pagination.ToContinuationToken(),
                Status = status,
                Top = pagination.top
            };
            var segment = await HackathonManagement.ListPaginatedEnrollmentsAsync(hackName, options, cancellationToken);
            var routeValues = new RouteValueDictionary();
            if (pagination.top.HasValue)
            {
                routeValues.Add(nameof(pagination.top), pagination.top.Value);
            }
            if (status.HasValue)
            {
                routeValues.Add(nameof(status), status.Value);
            }
            var nextLink = BuildNextLinkUrl(routeValues, segment.ContinuationToken);
            return Ok(ResponseBuilder.BuildResourceList<EnrollmentEntity, Enrollment, EnrollmentList>(
                    segment,
                    ResponseBuilder.BuildEnrollment,
                    nextLink));
        }

    }
}
