using Kaiyuanshe.OpenHackathon.Server.Auth;
using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.ResponseBuilder;
using Kaiyuanshe.OpenHackathon.Server.Storage;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
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
        /// <returns></returns>
        /// <response code="200">Success. The response describes a enrollment.</response>
        /// <response code="400">Bad Reqeuest. The response indicates the client request is not valid.</response>
        /// <response code="404">Not Found. The response indicates the hackathon or user is not found.</response>
        /// <response code="412">Precondition Failed. The response indicates enrollment is not started or ended.</response>
        [HttpPost]
        [ProducesResponseType(typeof(Enrollment), StatusCodes.Status200OK)]
        [Route("hackathon/{hackathonName}/enrollment")]
        [Authorize()]
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
        /// Approve a hackathon enrollement.
        /// </summary>
        /// <param name="parameter"></param>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="userId" example="1">Id of user</param>
        /// <returns></returns>
        /// <response code="200">Success. The enrollment is approved.</response>
        /// <response code="400">Bad Reqeuest. The response indicates the client request is not valid.</response>
        /// <response code="403">Forbidden. The response indicates the user doesn't have proper access.</response>
        /// <response code="404">Not Found. The response indicates the hackathon or user is not found.</response>
        [HttpPost]
        [ProducesResponseType(typeof(Enrollment), StatusCodes.Status200OK)]
        [Route("hackathon/{hackathonName}/enrollment/{userId}/approve")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.HackathonAdministrator)]
        public async Task<object> Approve(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required] string userId,
            [FromBody] Enrollment parameter)
        {
            return await UpdateEnrollmentStatus(hackathonName.ToLower(), userId.ToLower(), EnrollmentStatus.Approved);
        }

        /// <summary>
        /// Reject a hackathon enrollement.
        /// </summary>
        /// <param name="parameter"></param>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="userId" example="1">Id of user</param>
        /// <returns></returns>
        /// <response code="200">Success. The enrollment is approved.</response>
        /// <response code="400">Bad Reqeuest. The response indicates the client request is not valid.</response>
        /// <response code="403">Forbidden. The response indicates the user doesn't have proper access.</response>
        /// <response code="404">Not Found. The response indicates the hackathon or user is not found.</response>
        [HttpPost]
        [ProducesResponseType(typeof(Enrollment), StatusCodes.Status200OK)]
        [Route("hackathon/{hackathonName}/enrollment/{userId}/reject")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.HackathonAdministrator)]
        public async Task<object> Reject(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required] string userId,
            [FromBody] Enrollment parameter)
        {
            return await UpdateEnrollmentStatus(hackathonName.ToLower(), userId.ToLower(), EnrollmentStatus.Rejected);
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

            ParticipantEntity participant = await HackathonManagement.GetEnrollmentAsync(hackathonName, userId);
            if (participant == null || !participant.IsContestant())
            {
                return NotFound(string.Format(Resources.Hackathon_Enrollment_NotFound, userId, hackathonName));
            }

            participant = await HackathonManagement.UpdateEnrollmentStatusAsync(participant, status);
            return Ok(ResponseBuilder.BuildEnrollment(participant));
        }
    }
}
