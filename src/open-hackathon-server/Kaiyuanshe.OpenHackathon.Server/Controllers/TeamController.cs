using Kaiyuanshe.OpenHackathon.Server.Auth;
using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.ResponseBuilder;
using Kaiyuanshe.OpenHackathon.Server.Swagger;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Controllers
{
    /// <summary>
    /// controller to manage team
    /// </summary>
    public class TeamController : HackathonControllerBase
    {
        public IResponseBuilder ResponseBuilder { get; set; }

        public IHackathonManagement HackathonManagement { get; set; }

        public ITeamManagement TeamManagement { get; set; }

        /// <summary>
        /// Create a new team
        /// </summary>
        /// <param name="parameter"></param>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <returns>The enrollment</returns>
        /// <response code="200">Success. The response describes a enrollment.</response>
        [HttpPut]
        [ProducesResponseType(typeof(Team), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 404, 412)]
        [Route("hackathon/{hackathonName}/team")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.LoginUser)]
        public async Task<object> Create(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromBody] Team parameter,
            CancellationToken cancellationToken)
        {
            // validate hackathon
            var hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackathonName.ToLower(), cancellationToken);
            var options = new ValidateHackathonOptions
            {
                OnlineRequired = true,
                NotDeletedRequired = true,
                HackathonName = hackathonName,
            };
            if (await ValidateHackathon(hackathon, options, cancellationToken) == false)
            {
                return options.ValidateResult;
            }

            // validate enrollment
            var enrollment = await HackathonManagement.GetEnrollmentAsync(hackathonName.ToLower(), CurrentUserId, cancellationToken);
            var enrollmentOptions = new ValidateEnrollmentOptions
            {
                ApprovedRequired = true,
                HackathonName = hackathonName,
                UserId = CurrentUserId
            };
            if (ValidateEnrollment(enrollment, enrollmentOptions) == false)
            {
                return enrollmentOptions.ValidateResult;
            }

            // create team
            parameter.hackathonName = hackathonName.ToLower();
            parameter.creatorId = CurrentUserId;
            var teamEntity = await TeamManagement.CreateTeamAsync(parameter, cancellationToken);
            return Ok(ResponseBuilder.BuildTeam(teamEntity));
        }
    }
}
