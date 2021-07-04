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
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Controllers
{
    public class EnrollmentController : HackathonControllerBase
    {
        #region Enroll
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
                EnrollmentNotFullRequired = true,
                OnlineRequired = true,
                HackathonName = hackathonName,
            };
            if (await ValidateHackathon(hackathon, options, cancellationToken) == false)
            {
                return options.ValidateResult;
            }

            var enrollment = await EnrollmentManagement.GetEnrollmentAsync(hackathonName.ToLower(), CurrentUserId, cancellationToken);
            if (enrollment == null)
            {
                parameter.userId = CurrentUserId;
                enrollment = await EnrollmentManagement.CreateEnrollmentAsync(hackathon, parameter, cancellationToken);
                var user = await UserManagement.GetUserByIdAsync(CurrentUserId, cancellationToken);
                return Ok(ResponseBuilder.BuildEnrollment(enrollment, user));
            }
            else
            {
                // update
                return await UpdateInternalAsync(enrollment, parameter, cancellationToken);
            }
        }
        #endregion

        #region Update
        /// <summary>
        /// Update a enrollment. Cannot update the status, must call approve/reject API to update the status.
        /// </summary>
        /// <param name="parameter"></param>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="userId" example="1">Id of user</param>
        /// <returns>The enrollment</returns>
        /// <response code="200">Success. The response describes a enrollment.</response>
        [HttpPatch]
        [ProducesResponseType(typeof(Enrollment), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 403, 404)]
        [Route("hackathon/{hackathonName}/enrollment/{userId}")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.LoginUser)]
        public async Task<object> Update(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required] string userId,
            [FromBody] Enrollment parameter,
            CancellationToken cancellationToken)
        {
            HackathonEntity hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackathonName.ToLower());

            var options = new ValidateHackathonOptions
            {
                EnrollmentOpenRequired = true,
                OnlineRequired = true,
                HackathonName = hackathonName,
                HackAdminRequird = (userId != CurrentUserId),
            };
            if (await ValidateHackathon(hackathon, options, cancellationToken) == false)
            {
                return options.ValidateResult;
            }

            var enrollment = await EnrollmentManagement.GetEnrollmentAsync(hackathonName.ToLower(), userId, cancellationToken);
            if (enrollment == null)
            {
                return NotFound(string.Format(Resources.Enrollment_NotFound, userId, hackathonName));
            }

            return await UpdateInternalAsync(enrollment, parameter, cancellationToken);
        }


        private async Task<object> UpdateInternalAsync(EnrollmentEntity existing, Enrollment request, CancellationToken cancellationToken)
        {
            var extensions = existing.Extensions.Merge(request.extensions);
            if (extensions.Length > Enrollment.MaxExtensions)
            {
                return BadRequest(string.Format(Resources.Enrollment_TooManyExtensions, Enrollment.MaxExtensions));
            }

            var enrollment = await EnrollmentManagement.UpdateEnrollmentAsync(existing, request, cancellationToken);
            var user = await UserManagement.GetUserByIdAsync(existing.UserId, cancellationToken);
            return Ok(ResponseBuilder.BuildEnrollment(enrollment, user));
        }

        #endregion

        #region Get
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
        public async Task<object> Get(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            CancellationToken cancellationToken)
        {
            var enrollment = await EnrollmentManagement.GetEnrollmentAsync(hackathonName.ToLower(), CurrentUserId, cancellationToken);
            if (enrollment == null)
            {
                return NotFound(string.Format(Resources.Enrollment_NotFound, CurrentUserId, hackathonName));
            }
            var user = await UserManagement.GetUserByIdAsync(CurrentUserId, cancellationToken);
            return Ok(ResponseBuilder.BuildEnrollment(enrollment, user));
        }
        #endregion

        #region Approve && Reject
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
            [FromBody] Enrollment parameter,
            CancellationToken cancellationToken)
        {
            return await UpdateEnrollmentStatus(hackathonName.ToLower(), userId.ToLower(), EnrollmentStatus.approved, cancellationToken);
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
            [FromBody] Enrollment parameter,
            CancellationToken cancellationToken)
        {
            return await UpdateEnrollmentStatus(hackathonName.ToLower(), userId.ToLower(), EnrollmentStatus.rejected, cancellationToken);
        }

        private async Task<object> UpdateEnrollmentStatus(string hackathonName, string userId, EnrollmentStatus status, CancellationToken cancellationToken)
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


            EnrollmentEntity enrollment = await EnrollmentManagement.GetEnrollmentAsync(hackathonName, userId);
            if (enrollment == null)
            {
                return NotFound(string.Format(Resources.Enrollment_NotFound, userId, hackathonName));
            }

            enrollment = await EnrollmentManagement.UpdateEnrollmentStatusAsync(hackathon, enrollment, status);
            var user = await UserManagement.GetUserByIdAsync(CurrentUserId, cancellationToken);
            return Ok(ResponseBuilder.BuildEnrollment(enrollment, user));
        }
        #endregion

        #region GetById
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
            [FromRoute, Required] string userId,
            CancellationToken cancellationToken)
        {
            var hackName = hackathonName.ToLower();
            HackathonEntity hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackName, cancellationToken);
            var options = new ValidateHackathonOptions
            {
                HackathonName = hackathonName,
                UserId = userId,
                WritableRequired = false,
            };
            if (await ValidateHackathon(hackathon, options) == false)
            {
                return options.ValidateResult;
            }

            EnrollmentEntity enrollment = await EnrollmentManagement.GetEnrollmentAsync(hackName, userId.ToLower(), cancellationToken);
            if (enrollment == null)
            {
                return NotFound(string.Format(Resources.Enrollment_NotFound, userId, hackathonName));
            }
            var user = await UserManagement.GetUserByIdAsync(CurrentUserId, cancellationToken);
            return Ok(ResponseBuilder.BuildEnrollment(enrollment, user));
        }
        #endregion

        #region ListEnrollments
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
            HackathonEntity hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackName, cancellationToken);
            var options = new ValidateHackathonOptions
            {
                HackathonName = hackathonName,
                WritableRequired = false,
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
            var segment = await EnrollmentManagement.ListPaginatedEnrollmentsAsync(hackName, enrollmentOptions, cancellationToken);
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

            List<Tuple<EnrollmentEntity, UserInfo>> list = new List<Tuple<EnrollmentEntity, UserInfo>>();
            foreach (var enrollment in segment)
            {
                var user = await UserManagement.GetUserByIdAsync(enrollment.UserId, cancellationToken);
                list.Add(Tuple.Create(enrollment, user));
            }

            return Ok(ResponseBuilder.BuildResourceList<EnrollmentEntity, UserInfo, Enrollment, EnrollmentList>(
                    list,
                    ResponseBuilder.BuildEnrollment,
                    nextLink));
        }
        #endregion
    }
}
