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
        [HttpPut]
        [ProducesResponseType(typeof(Enrollment), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 404, 412)]
        [Route("hackathon/{hackathonName}/enrollment")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.LoginUser)]
        public async Task<object> Enroll(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromBody] Enrollment parameter,
            CancellationToken cancellationToken)
        {
            HackathonEntity hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackathonName.ToLower());

            var options = new ValidateHackathonOptions
            {
                EnrollmentOpenRequired = true,
                OnlineRequired = true,
                HackathonName = hackathonName,
            };
            if (await ValidateHackathon(hackathon, options, cancellationToken) == false)
            {
                return options.ValidateResult;
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
                return NotFound(string.Format(Resources.Enrollment_NotFound, CurrentUserId, hackathonName));
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
            var options = new ValidateHackathonOptions
            {
                HackAdminRequird = true,
                HackathonName = hackathonName,
            };
            if (await ValidateHackathon(hackathon, options) == false)
            {
                return options.ValidateResult;
            }

            EnrollmentEntity enrollment = await HackathonManagement.GetEnrollmentAsync(hackathonName, userId);
            if (enrollment == null)
            {
                return NotFound(string.Format(Resources.Enrollment_NotFound, userId, hackathonName));
            }

            enrollment = await HackathonManagement.UpdateEnrollmentStatusAsync(enrollment, status);
            return Ok(ResponseBuilder.BuildEnrollment(enrollment));
        }

        /// <summary>
        /// Get a hackathon enrollement of any enrolled user.
        /// </summary>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="userId" example="1">Id of user</param>
        /// <returns>The enrollment</returns>
        /// <response code="200">Success.</response>
        [HttpGet]
        [ProducesResponseType(typeof(Enrollment), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 404)]
        [Route("hackathon/{hackathonName}/enrollment/{userId}")]
        public async Task<object> GetById(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required] string userId)
        {
            var hackName = hackathonName.ToLower();
            HackathonEntity hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackName);
            var options = new ValidateHackathonOptions
            {
                UserId = CurrentUserId,
                HackathonName = hackathonName,
            };
            if (await ValidateHackathon(hackathon, options) == false)
            {
                return options.ValidateResult;
            }

            EnrollmentEntity enrollment = await HackathonManagement.GetEnrollmentAsync(hackName, userId.ToLower());
            if (enrollment == null)
            {
                return NotFound(string.Format(Resources.Enrollment_NotFound, userId, hackathonName));
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
        [SwaggerErrorResponse(400, 404)]
        [Route("hackathon/{hackathonName}/enrollments")]
        public async Task<object> ListEnrollments(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromQuery] Pagination pagination,
            [FromQuery] EnrollmentStatus? status,
            CancellationToken cancellationToken)
        {
            var hackName = hackathonName.ToLower();
            HackathonEntity hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackName);
            var options = new ValidateHackathonOptions
            {
                UserId = CurrentUserId,
                HackathonName = hackathonName,
            };
            if (await ValidateHackathon(hackathon, options) == false)
            {
                return options.ValidateResult;
            }

            var enrollmentOptions = new EnrollmentQueryOptions
            {
                TableContinuationToken = pagination.ToContinuationToken(),
                Status = status,
                Top = pagination.top
            };
            var segment = await HackathonManagement.ListPaginatedEnrollmentsAsync(hackName, enrollmentOptions, cancellationToken);
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
