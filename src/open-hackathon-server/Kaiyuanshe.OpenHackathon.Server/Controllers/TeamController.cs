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
        /// List paginated teams of a hackathon.
        /// </summary>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <returns>the response contains a list of teams and a nextLink if there are more results.</returns>
        /// <response code="200">Success.</response>
        [HttpGet]
        [ProducesResponseType(typeof(TeamList), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 404)]
        [Route("hackathon/{hackathonName}/teams")]
        public async Task<object> ListTeams(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromQuery] Pagination pagination,
            CancellationToken cancellationToken)
        {
            var hackName = hackathonName.ToLower();
            var hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackName);
            var options = new ValidateHackathonOptions
            {
                HackathonName = hackathonName,
            };
            if (await ValidateHackathon(hackathon, options) == false)
            {
                return options.ValidateResult;
            }

            var teamQueryOptions = new TeamQueryOptions
            {
                TableContinuationToken = pagination.ToContinuationToken(),
                Top = pagination.top
            };
            var segment = await TeamManagement.ListPaginatedTeamsAsync(hackName, teamQueryOptions, cancellationToken);
            var routeValues = new RouteValueDictionary();
            if (pagination.top.HasValue)
            {
                routeValues.Add(nameof(pagination.top), pagination.top.Value);
            }
            var nextLink = BuildNextLinkUrl(routeValues, segment.ContinuationToken);
            return Ok(ResponseBuilder.BuildResourceList<TeamEntity, Team, TeamList>(
                    segment,
                    ResponseBuilder.BuildTeam,
                    nextLink));
        }

        /// <summary>
        /// Delete a team
        /// </summary>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="teamId" example="d1e40c38-cc2a-445f-9eab-60c253256c57">unique Guid of the team. Auto-generated on server side.</param>
        /// <returns></returns>
        /// <response code="204">Deleted. The response indicates the team is removed.</response>
        [HttpDelete]
        [SwaggerErrorResponse(400, 403, 412)]
        [Route("hackathon/{hackathonName}/team/{teamId}")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.TeamAdministrator)]
        public async Task<object> DeleteTeam(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required, StringLength(36, MinimumLength = 36)] string teamId,
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

            // Validate team
            var team = await TeamManagement.GetTeamByIdAsync(hackathonName.ToLower(), teamId, cancellationToken);
            if (team == null)
            {
                return NoContent();
            }
            var teamValidateOptions = new ValidateTeamOptions
            {
                TeamAdminRequired = true,
            };
            if (await ValidateTeam(team, teamValidateOptions) == false)
            {
                return teamValidateOptions.ValidateResult;
            }

            // Delete team
            await TeamManagement.DeleteTeamAsync(team, cancellationToken);
            return NoContent();
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
        public async Task<object> JoinTeam(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required, StringLength(36, MinimumLength = 36)] string teamId,
            [FromBody] TeamMember parameter,
            CancellationToken cancellationToken)
        {
            return await AddTeamMemberInternalAsync(hackathonName.ToLower(), teamId, CurrentUserId, parameter, false, cancellationToken);
        }

        /// <summary>
        /// Add a new member to a team by team admin
        /// </summary>
        /// <param name="parameter"></param>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="teamId" example="d1e40c38-cc2a-445f-9eab-60c253256c57">unique Guid of the team. Auto-generated on server side.</param>
        /// <param name="userId" example="1">Id of user</param>
        /// <returns>The team member</returns>
        /// <response code="200">Success. The response describes a team member.</response>
        [HttpPut]
        [ProducesResponseType(typeof(TeamMember), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 403, 404, 412)]
        [Route("hackathon/{hackathonName}/team/{teamId}/member/{userId}")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.TeamAdministrator)]
        public async Task<object> AddTeamMember(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required, StringLength(36, MinimumLength = 36)] string teamId,
            [FromRoute, Required] string userId,
            [FromBody] TeamMember parameter,
            CancellationToken cancellationToken)
        {
            return await AddTeamMemberInternalAsync(hackathonName.ToLower(), teamId, userId, parameter, true, cancellationToken);
        }

        private async Task<object> AddTeamMemberInternalAsync(string hackathonName, string teamId,
            string userId, TeamMember parameter, bool teamAdminRequired, CancellationToken cancellationToken)
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
            var enrollment = await HackathonManagement.GetEnrollmentAsync(hackathonName.ToLower(), userId, cancellationToken);
            var enrollmentOptions = new ValidateEnrollmentOptions
            {
                ApprovedRequired = true,
                HackathonName = hackathonName,
                UserId = userId,
            };
            if (ValidateEnrollment(enrollment, enrollmentOptions) == false)
            {
                return enrollmentOptions.ValidateResult;
            }

            // Validate team
            var team = await TeamManagement.GetTeamByIdAsync(hackathonName.ToLower(), teamId, cancellationToken);
            var teamValidateOptions = new ValidateTeamOptions
            {
                TeamAdminRequired = teamAdminRequired,
            };
            if (await ValidateTeam(team, teamValidateOptions) == false)
            {
                return teamValidateOptions.ValidateResult;
            }

            // join team
            var teamMember = await TeamManagement.GetTeamMemberAsync(teamId, userId, cancellationToken);
            if (teamMember == null)
            {
                parameter.hackathonName = hackathonName.ToLower();
                parameter.teamId = team.Id;
                parameter.userId = userId;
                parameter.status = TeamMemberStatus.pendingApproval;
                if (team.AutoApprove || teamAdminRequired)
                {
                    parameter.status = TeamMemberStatus.approved;
                }
                teamMember = await TeamManagement.CreateTeamMemberAsync(parameter, cancellationToken);
            }
            else
            {
                teamMember = await TeamManagement.UpdateTeamMemberAsync(teamMember, parameter, cancellationToken);
            }
            return Ok(ResponseBuilder.BuildTeamMember(teamMember));
        }

        /// <summary>
        /// Update a team member information. Not including the Role/Status. Call other APIs to update Role/Status.
        /// </summary>
        /// <param name="parameter"></param>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="teamId" example="d1e40c38-cc2a-445f-9eab-60c253256c57">unique Guid of the team. Auto-generated on server side.</param>
        /// <param name="userId" example="1">Id of user</param>
        /// <returns>The updated team member</returns>
        /// <response code="200">Success. The response describes a team member.</response>
        [HttpPatch]
        [ProducesResponseType(typeof(TeamMember), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 403, 404)]
        [Route("hackathon/{hackathonName}/team/{teamId}/member/{userId}")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.TeamMember)]
        public async Task<object> UpdateTeamMember(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required, StringLength(36, MinimumLength = 36)] string teamId,
            [FromRoute, Required] string userId,
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

            // Validate team and member
            var team = await TeamManagement.GetTeamByIdAsync(hackathonName.ToLower(), teamId.ToLower(), cancellationToken);
            var teamMember = await TeamManagement.GetTeamMemberAsync(teamId.ToLower(), userId, cancellationToken);
            var teamMemberValidateOption = new ValidateTeamMemberOptions
            {
                TeamId = teamId,
                UserId = userId,
                ApprovedMemberRequired = true
            };
            if (await ValidateTeamMember(team, teamMember, teamMemberValidateOption, cancellationToken) == false)
            {
                return teamMemberValidateOption.ValidateResult;
            }

            // Update team member
            teamMember = await TeamManagement.UpdateTeamMemberAsync(teamMember, parameter, cancellationToken);
            return Ok(ResponseBuilder.BuildTeamMember(teamMember));
        }

        /// <summary>
        /// Approve a team member
        /// </summary>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="teamId" example="d1e40c38-cc2a-445f-9eab-60c253256c57">unique Guid of the team. Auto-generated on server side.</param>
        /// <param name="userId" example="1">Id of user</param>
        /// <returns>The updated team member</returns>
        /// <response code="200">Success. The response describes a team member.</response>
        [HttpPost]
        [ProducesResponseType(typeof(TeamMember), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 403, 404)]
        [Route("hackathon/{hackathonName}/team/{teamId}/member/{userId}/approve")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.TeamAdministrator)]
        public async Task<object> ApproveTeamMember(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required, StringLength(36, MinimumLength = 36)] string teamId,
            [FromRoute, Required] string userId,
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

            // Validate team
            var team = await TeamManagement.GetTeamByIdAsync(hackathonName.ToLower(), teamId, cancellationToken);
            var teamValidateOptions = new ValidateTeamOptions
            {
                TeamAdminRequired = true
            };
            if (await ValidateTeam(team, teamValidateOptions) == false)
            {
                return teamValidateOptions.ValidateResult;
            }

            // Validate team member
            var teamMember = await TeamManagement.GetTeamMemberAsync(teamId.ToLower(), userId, cancellationToken);
            var teamMemberValidateOption = new ValidateTeamMemberOptions
            {
                TeamId = teamId,
                UserId = userId,
            };
            if (await ValidateTeamMember(team, teamMember, teamMemberValidateOption, cancellationToken) == false)
            {
                return teamMemberValidateOption.ValidateResult;
            }

            // update status
            teamMember = await TeamManagement.UpdateTeamMemberStatusAsync(teamMember, TeamMemberStatus.approved, cancellationToken);
            return Ok(ResponseBuilder.BuildTeamMember(teamMember));
        }

        /// <summary>
        /// Change role of a team member
        /// </summary>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="teamId" example="d1e40c38-cc2a-445f-9eab-60c253256c57">unique Guid of the team. Auto-generated on server side.</param>
        /// <param name="userId" example="1">Id of user</param>
        /// <returns>The updated team member</returns>
        /// <response code="200">Success. The response describes a team member.</response>
        [HttpPost]
        [ProducesResponseType(typeof(TeamMember), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 403, 404)]
        [Route("hackathon/{hackathonName}/team/{teamId}/member/{userId}/updateRole")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.TeamAdministrator)]
        public async Task<object> UpdateTeamMemberRole(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required, StringLength(36, MinimumLength = 36)] string teamId,
            [FromRoute, Required] string userId,
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

            // Validate team
            var team = await TeamManagement.GetTeamByIdAsync(hackathonName.ToLower(), teamId, cancellationToken);
            var teamValidateOptions = new ValidateTeamOptions
            {
                TeamAdminRequired = true
            };
            if (await ValidateTeam(team, teamValidateOptions) == false)
            {
                return teamValidateOptions.ValidateResult;
            }

            // Validate team member
            var teamMember = await TeamManagement.GetTeamMemberAsync(teamId.ToLower(), userId, cancellationToken);
            var teamMemberValidateOption = new ValidateTeamMemberOptions
            {
                TeamId = teamId,
                UserId = userId,
            };
            if (await ValidateTeamMember(team, teamMember, teamMemberValidateOption, cancellationToken) == false)
            {
                return teamMemberValidateOption.ValidateResult;
            }

            // update status
            teamMember = await TeamManagement.UpdateTeamMemberRoleAsync(teamMember, parameter.role.GetValueOrDefault(teamMember.Role), cancellationToken);
            return Ok(ResponseBuilder.BuildTeamMember(teamMember));
        }

        /// <summary>
        /// Leave a team
        /// </summary>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="teamId" example="d1e40c38-cc2a-445f-9eab-60c253256c57">unique Guid of the team. Auto-generated on server side.</param>
        /// <returns></returns>
        /// <response code="204">Deleted. The response indicates the member is removed from the team.</response>
        [HttpDelete]
        [SwaggerErrorResponse(400, 404, 412)]
        [Route("hackathon/{hackathonName}/team/{teamId}/member")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.LoginUser)]
        public async Task<object> LeaveTeam(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required, StringLength(36, MinimumLength = 36)] string teamId,
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

            // Validate team
            var team = await TeamManagement.GetTeamByIdAsync(hackathonName.ToLower(), teamId, cancellationToken);
            var teamValidateOptions = new ValidateTeamOptions
            {
            };
            if (await ValidateTeam(team, teamValidateOptions) == false)
            {
                return teamValidateOptions.ValidateResult;
            }

            // Delete team member
            return await DeleteMemberInternalAsync(teamId.ToLower(), CurrentUserId, cancellationToken);
        }

        /// <summary>
        /// Remove a team member or reject a team member joining request.  Team Admin only.
        /// </summary>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="teamId" example="d1e40c38-cc2a-445f-9eab-60c253256c57">unique Guid of the team. Auto-generated on server side.</param>
        /// <param name="userId" example="1">Id of user</param>
        /// <returns></returns>
        /// <response code="204">Deleted. The response indicates the member is removed from the team.</response>
        [HttpDelete]
        [SwaggerErrorResponse(400, 403, 404, 412)]
        [Route("hackathon/{hackathonName}/team/{teamId}/member/{userId}")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.TeamAdministrator)]
        public async Task<object> DeleteTeamMember(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required, StringLength(36, MinimumLength = 36)] string teamId,
             [FromRoute, Required] string userId,
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

            // Validate team
            var team = await TeamManagement.GetTeamByIdAsync(hackathonName.ToLower(), teamId, cancellationToken);
            var teamValidateOptions = new ValidateTeamOptions
            {
                TeamAdminRequired = true,
            };
            if (await ValidateTeam(team, teamValidateOptions) == false)
            {
                return teamValidateOptions.ValidateResult;
            }

            // Delete team member
            return await DeleteMemberInternalAsync(teamId.ToLower(), userId, cancellationToken);
        }

        private async Task<object> DeleteMemberInternalAsync(string teamId, string userId, CancellationToken cancellationToken)
        {
            var teamMember = await TeamManagement.GetTeamMemberAsync(teamId, userId, cancellationToken);
            if (teamMember == null)
            {
                // deleted already
                return NoContent();
            }

            // one of the admins must be the last person who leaves the team, to ensure there is at least one admin at any time.
            var members = await TeamManagement.ListTeamMembersAsync(teamId, cancellationToken);
            var admins = members.Where(m => m.Role == TeamMemberRole.Admin && m.Status == TeamMemberStatus.approved);
            if (admins.Count() == 1 && members.Count() > 1 && admins.Single().UserId == userId)
            {
                return PreconditionFailed(Resources.TeamMember_LastAdmin);
            }

            // remove it
            await TeamManagement.DeleteTeamMemberAsync(teamMember, cancellationToken);
            return NoContent();
        }

        /// <summary>
        /// Query a team member
        /// </summary>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="teamId" example="d1e40c38-cc2a-445f-9eab-60c253256c57">unique Guid of the team. Auto-generated on server side.</param>
        /// <param name="userId" example="1">Id of user</param>
        /// <returns>The team member</returns>
        /// <response code="200">Success. The response describes a team member.</response>
        [HttpGet]
        [ProducesResponseType(typeof(TeamMember), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 404)]
        [Route("hackathon/{hackathonName}/team/{teamId}/member/{userId}")]
        public async Task<object> GetTeamMember(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required, StringLength(36, MinimumLength = 36)] string teamId,
            [FromRoute, Required] string userId,
            CancellationToken cancellationToken)
        {
            // validate hackathon
            var hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackathonName.ToLower(), cancellationToken);
            var options = new ValidateHackathonOptions
            {
                HackathonName = hackathonName,
            };
            if (await ValidateHackathon(hackathon, options, cancellationToken) == false)
            {
                return options.ValidateResult;
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

            // Validate team member
            var teamMember = await TeamManagement.GetTeamMemberAsync(teamId.ToLower(), userId, cancellationToken);
            var teamMemberValidateOption = new ValidateTeamMemberOptions
            {
                TeamId = teamId,
                UserId = userId,
            };
            if (await ValidateTeamMember(team, teamMember, teamMemberValidateOption, cancellationToken) == false)
            {
                return teamMemberValidateOption.ValidateResult;
            }

            return Ok(ResponseBuilder.BuildTeamMember(teamMember));
        }
    }
}
