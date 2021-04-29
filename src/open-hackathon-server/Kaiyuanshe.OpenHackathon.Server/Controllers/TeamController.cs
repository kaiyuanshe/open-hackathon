using Kaiyuanshe.OpenHackathon.Server.Auth;
using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.ResponseBuilder;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
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
        /// <returns>The team</returns>
        /// <response code="200">Success. The response describes a team.</response>
        [HttpPut]
        [ProducesResponseType(typeof(Team), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 404, 412)]
        [Route("hackathon/{hackathonName}/team")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.LoginUser)]
        public async Task<object> CreateTeam(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromBody] Team parameter,
            CancellationToken cancellationToken)
        {
            // validate hackathon
            var hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackathonName.ToLower(), cancellationToken);
            var options = new ValidateHackathonOptions
            {
                OnlineRequired = true,
                HackathonOpenRequired = true,
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

        /// <summary>
        /// Update a new team
        /// </summary>
        /// <param name="parameter"></param>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="teamId" example="d1e40c38-cc2a-445f-9eab-60c253256c57">unique Guid of the team. Auto-generated on server side.</param>
        /// <returns>The updated team</returns>
        /// <response code="200">Success. The response describes a team.</response>
        [HttpPatch]
        [ProducesResponseType(typeof(Team), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 403, 404)]
        [Route("hackathon/{hackathonName}/team/{teamId}")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.TeamAdministrator)]
        public async Task<object> UpdateTeam(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required, StringLength(36, MinimumLength = 36)] string teamId,
            [FromBody] Team parameter,
            CancellationToken cancellationToken)
        {
            // validate hackathon
            var hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackathonName.ToLower(), cancellationToken);
            var options = new ValidateHackathonOptions
            {
                OnlineRequired = true,
                HackathonOpenRequired = true,
                HackathonName = hackathonName,
                UserId = CurrentUserId,
            };
            if (await ValidateHackathon(hackathon, options, cancellationToken) == false)
            {
                return options.ValidateResult;
            }

            // validate team
            var team = await TeamManagement.GetTeamByIdAsync(hackathonName.ToLower(), teamId, cancellationToken);
            var teamOptions = new ValidateTeamOptions
            {
                TeamAdminRequired = true,
            };
            if (!await ValidateTeam(team, teamOptions, cancellationToken))
            {
                return teamOptions.ValidateResult;
            }

            team = await TeamManagement.UpdateTeamAsync(parameter, team, cancellationToken);
            return Ok(ResponseBuilder.BuildTeam(team));
        }

        /// <summary>
        /// Get a team
        /// </summary>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="teamId" example="d1e40c38-cc2a-445f-9eab-60c253256c57">unique Guid of the team. Auto-generated on server side.</param>
        /// <returns>The updated team</returns>
        /// <response code="200">Success. The response describes a team.</response>
        [HttpGet]
        [ProducesResponseType(typeof(Team), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 404)]
        [Route("hackathon/{hackathonName}/team/{teamId}")]
        public async Task<object> GetTeam(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required, StringLength(36, MinimumLength = 36)] string teamId,
            CancellationToken cancellationToken)
        {
            // validate hackathon
            var hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackathonName.ToLower(), cancellationToken);
            var options = new ValidateHackathonOptions
            {
                HackathonName = hackathonName,
                UserId = CurrentUserId,
            };
            if (await ValidateHackathon(hackathon, options, cancellationToken) == false)
            {
                return options.ValidateResult;
            }

            // validate team
            var team = await TeamManagement.GetTeamByIdAsync(hackathonName.ToLower(), teamId, cancellationToken);
            var teamOptions = new ValidateTeamOptions
            {
            };
            if (!await ValidateTeam(team, teamOptions, cancellationToken))
            {
                return teamOptions.ValidateResult;
            }

            return Ok(ResponseBuilder.BuildTeam(team));
        }

        /// <summary>
        /// Join a team after enrolled
        /// </summary>
        /// <param name="parameter"></param>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="teamId" example="d1e40c38-cc2a-445f-9eab-60c253256c57">unique Guid of the team. Auto-generated on server side.</param>
        /// <returns>The team member</returns>
        /// <response code="200">Success. The response describes a team member.</response>
        [HttpPut]
        [ProducesResponseType(typeof(TeamMember), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 404, 412)]
        [Route("hackathon/{hackathonName}/team/{teamId}/member")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.LoginUser)]
        public async Task<object> CreateTeamMember(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required, StringLength(36, MinimumLength = 36)] string teamId,
            [FromBody] TeamMember parameter,
            CancellationToken cancellationToken)
        {
            // validate hackathon
            var hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackathonName.ToLower(), cancellationToken);
            var options = new ValidateHackathonOptions
            {
                OnlineRequired = true,
                HackathonOpenRequired = true,
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

            // Validate team
            var team = await TeamManagement.GetTeamByIdAsync(hackathonName.ToLower(), teamId, cancellationToken);
            var teamValidateOptions = new ValidateTeamOptions
            {
            };
            if (await ValidateTeam(team, teamValidateOptions) == false)
            {
                return teamValidateOptions.ValidateResult;
            }

            // join team
            var teamMember = await TeamManagement.GetTeamMemberAsync(teamId, CurrentUserId, cancellationToken);
            if (teamMember == null)
            {
                parameter.hackathonName = hackathonName.ToLower();
                parameter.teamId = team.Id;
                parameter.userId = CurrentUserId;
                teamMember = await TeamManagement.CreateTeamMemberAsync(team, parameter, cancellationToken);
            }
            else
            {
                teamMember = await TeamManagement.UpdateTeamMemberAsync(teamMember, parameter, cancellationToken);
            }
            return Ok(ResponseBuilder.BuildTeamMember(teamMember));
        }
    }
}
