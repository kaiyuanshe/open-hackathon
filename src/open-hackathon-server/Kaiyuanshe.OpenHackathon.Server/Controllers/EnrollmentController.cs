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
        [HttpPut]
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
    }
}
