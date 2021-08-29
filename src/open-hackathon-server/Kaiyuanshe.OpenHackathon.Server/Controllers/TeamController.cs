using Kaiyuanshe.OpenHackathon.Server.Auth;
using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Models.Validations;
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
    /// <summary>
    /// controller to manage team
    /// </summary>
    public class TeamController : HackathonControllerBase
    {
        #region CreateTeam
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
            var enrollment = await EnrollmentManagement.GetEnrollmentAsync(hackathonName.ToLower(), CurrentUserId, cancellationToken);
            var enrollmentOptions = new ValidateEnrollmentOptions
            {
                ApprovedRequired = true,
                HackathonName = hackathonName,
            };
            if (ValidateEnrollment(enrollment, enrollmentOptions) == false)
            {
                return enrollmentOptions.ValidateResult;
            }

            // Check name exitance
            if (await IsTeamNameTaken(hackathonName.ToLower(), parameter.displayName, cancellationToken))
            {
                return PreconditionFailed(string.Format(Resources.Team_NameTaken, parameter.displayName));
            }

            // check team membership
            var teamMember = await TeamManagement.GetTeamMemberAsync(hackathonName.ToLower(), CurrentUserId, default);
            if (teamMember != null)
            {
                return PreconditionFailed(Resources.Team_CreateSecond);
            }

            // create team
            parameter.hackathonName = hackathonName.ToLower();
            parameter.creatorId = CurrentUserId;
            var teamEntity = await TeamManagement.CreateTeamAsync(parameter, cancellationToken);
            var creator = await GetCurrentUserInfo(cancellationToken);
            return Ok(ResponseBuilder.BuildTeam(teamEntity, creator));
        }

        private async Task<bool> IsTeamNameTaken(string hackathonName, string teamName, CancellationToken cancellationToken)
        {
            var teams = await TeamManagement.GetTeamByNameAsync(hackathonName, teamName, cancellationToken);
            return teams.Count() > 0;
        }
        #endregion

        #region UpdateTeam
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
            [FromRoute, Required, Guid] string teamId,
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
            // check name uniqueness
            if (parameter.displayName != null && team.DisplayName != parameter.displayName)
            {
                if (await IsTeamNameTaken(hackathonName.ToLower(), parameter.displayName, cancellationToken))
                {
                    return PreconditionFailed(string.Format(Resources.Team_NameTaken, parameter.displayName));
                }
            }

            team = await TeamManagement.UpdateTeamAsync(parameter, team, cancellationToken);
            var creator = await UserManagement.GetUserByIdAsync(team.CreatorId, cancellationToken);
            return Ok(ResponseBuilder.BuildTeam(team, creator));
        }
        #endregion

        #region GetTeam
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
            [FromRoute, Required, Guid] string teamId,
            CancellationToken cancellationToken)
        {
            // validate hackathon
            var hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackathonName.ToLower(), cancellationToken);
            var options = new ValidateHackathonOptions
            {
                HackathonName = hackathonName,
                UserId = CurrentUserId,
                WritableRequired = false,
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

            var creator = await UserManagement.GetUserByIdAsync(team.CreatorId, cancellationToken);
            return Ok(ResponseBuilder.BuildTeam(team, creator));
        }
        #endregion

        #region ListTeams
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
                WritableRequired = false,
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

            List<Tuple<TeamEntity, UserInfo>> tuples = new List<Tuple<TeamEntity, UserInfo>>();
            foreach (var team in segment)
            {
                var creator = await UserManagement.GetUserByIdAsync(team.CreatorId, cancellationToken);
                tuples.Add(Tuple.Create(team, creator));
            }
            return Ok(ResponseBuilder.BuildResourceList<TeamEntity, UserInfo, Team, TeamList>(
                    tuples,
                    ResponseBuilder.BuildTeam,
                    nextLink));
        }
        #endregion

        #region DeleteTeam
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
            [FromRoute, Required, Guid] string teamId,
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
                NoAwardAssignmentRequired = true,
                NoRatingRequired = true,
            };
            if (await ValidateTeam(team, teamValidateOptions) == false)
            {
                return teamValidateOptions.ValidateResult;
            }

            // Delete team and member
            var members = await TeamManagement.ListTeamMembersAsync(hackathonName.ToLower(), teamId, cancellationToken);
            foreach (var member in members)
            {
                await TeamManagement.DeleteTeamMemberAsync(member, cancellationToken);
            }
            await TeamManagement.DeleteTeamAsync(team, cancellationToken);
            return NoContent();
        }
        #endregion

        #region JoinTeam
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
            [FromRoute, Required, Guid] string teamId,
            [FromBody] TeamMember parameter,
            CancellationToken cancellationToken)
        {
            return await AddTeamMemberInternalAsync(hackathonName.ToLower(), teamId, CurrentUserId, parameter, false, cancellationToken);
        }
        #endregion

        #region AddTeamMember
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
            [FromRoute, Required, Guid] string teamId,
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
            var enrollment = await EnrollmentManagement.GetEnrollmentAsync(hackathonName.ToLower(), userId, cancellationToken);
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
            var teamMember = await TeamManagement.GetTeamMemberAsync(hackathonName.ToLower(), userId, cancellationToken);
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

            var user = await UserManagement.GetUserByIdAsync(userId, cancellationToken);
            return Ok(ResponseBuilder.BuildTeamMember(teamMember, user));
        }
        #endregion

        #region UpdateTeamMember
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
            [FromRoute, Required, Guid] string teamId,
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
            var teamMember = await TeamManagement.GetTeamMemberAsync(hackathonName.ToLower(), userId, cancellationToken);
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
            var user = await UserManagement.GetUserByIdAsync(userId, cancellationToken);
            return Ok(ResponseBuilder.BuildTeamMember(teamMember, user));
        }
        #endregion

        #region ApproveTeamMember
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
            [FromRoute, Required, Guid] string teamId,
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
            var teamMember = await TeamManagement.GetTeamMemberAsync(hackathonName.ToLower(), userId, cancellationToken);
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
            var user = await UserManagement.GetUserByIdAsync(userId, cancellationToken);
            return Ok(ResponseBuilder.BuildTeamMember(teamMember, user));
        }
        #endregion

        #region UpdateTeamMemberRole
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
            [FromRoute, Required, Guid] string teamId,
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
            var teamMember = await TeamManagement.GetTeamMemberAsync(hackathonName.ToLower(), userId, cancellationToken);
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
            var user = await UserManagement.GetUserByIdAsync(userId, cancellationToken);
            return Ok(ResponseBuilder.BuildTeamMember(teamMember, user));
        }
        #endregion

        #region LeaveTeam
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
            [FromRoute, Required, Guid] string teamId,
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
            return await DeleteMemberInternalAsync(hackathonName.ToLower(), teamId.ToLower(), CurrentUserId, cancellationToken);
        }
        #endregion

        #region DeleteTeamMember
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
            [FromRoute, Required, Guid] string teamId,
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
            return await DeleteMemberInternalAsync(hackathonName.ToLower(), teamId.ToLower(), userId, cancellationToken);
        }

        private async Task<object> DeleteMemberInternalAsync(string hackathonName, string teamId, string userId, CancellationToken cancellationToken)
        {
            var teamMember = await TeamManagement.GetTeamMemberAsync(hackathonName, userId, cancellationToken);
            if (teamMember == null)
            {
                // deleted already
                return NoContent();
            }

            // one of the admins must be the last person who leaves the team, to ensure there is at least one admin at any time.
            var members = await TeamManagement.ListTeamMembersAsync(hackathonName, teamId, cancellationToken);
            var admins = members.Where(m => m.Role == TeamMemberRole.Admin && m.Status == TeamMemberStatus.approved);
            if (admins.Count() == 1 && members.Count() > 1 && admins.Single().UserId == userId)
            {
                return PreconditionFailed(Resources.TeamMember_LastAdmin);
            }

            // remove it
            await TeamManagement.DeleteTeamMemberAsync(teamMember, cancellationToken);
            return NoContent();
        }
        #endregion

        #region GetTeamMember
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
            [FromRoute, Required, Guid] string teamId,
            [FromRoute, Required] string userId,
            CancellationToken cancellationToken)
        {
            // validate hackathon
            var hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackathonName.ToLower(), cancellationToken);
            var options = new ValidateHackathonOptions
            {
                HackathonName = hackathonName,
                WritableRequired = false,
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
            var teamMember = await TeamManagement.GetTeamMemberAsync(hackathonName.ToLower(), userId, cancellationToken);
            var teamMemberValidateOption = new ValidateTeamMemberOptions
            {
                TeamId = teamId,
                UserId = userId,
            };
            if (await ValidateTeamMember(team, teamMember, teamMemberValidateOption, cancellationToken) == false)
            {
                return teamMemberValidateOption.ValidateResult;
            }

            var user = await UserManagement.GetUserByIdAsync(userId, cancellationToken);
            return Ok(ResponseBuilder.BuildTeamMember(teamMember, user));
        }
        #endregion

        #region ListMembers
        /// <summary>
        /// List paginated members of a team.
        /// </summary>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="teamId" example="d1e40c38-cc2a-445f-9eab-60c253256c57">unique Guid of the team. Auto-generated on server side.</param>
        /// <param name="status" example="approved">optional filter by member status.</param>
        /// <param name="role" example="member">optional filter by role of team member. </param>
        /// <returns>the response contains a list of team members and a nextLink if there are more results.</returns>
        /// <response code="200">Success.</response>
        [HttpGet]
        [ProducesResponseType(typeof(TeamMemberList), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 404)]
        [Route("hackathon/{hackathonName}/team/{teamId}/members")]
        public async Task<object> ListMembers(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required, Guid] string teamId,
            [FromQuery] Pagination pagination,
            [FromQuery] TeamMemberRole? role,
            [FromQuery] TeamMemberStatus? status,
            CancellationToken cancellationToken)
        {
            // validate hackathon
            var hackName = hackathonName.ToLower();
            HackathonEntity hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackName);
            var options = new ValidateHackathonOptions
            {
                HackathonName = hackathonName,
                WritableRequired = false,
            };
            if (await ValidateHackathon(hackathon, options) == false)
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

            // list
            var qureyOptions = new TeamMemberQueryOptions
            {
                TableContinuationToken = pagination.ToContinuationToken(),
                Status = status,
                Role = role,
                Top = pagination.top
            };
            var segment = await TeamManagement.ListPaginatedTeamMembersAsync(hackathonName.ToLower(), teamId, qureyOptions, cancellationToken);
            var routeValues = new RouteValueDictionary();
            if (pagination.top.HasValue)
            {
                routeValues.Add(nameof(pagination.top), pagination.top.Value);
            }
            if (status.HasValue)
            {
                routeValues.Add(nameof(status), status.Value);
            }
            if (role.HasValue)
            {
                routeValues.Add(nameof(role), role.Value);
            }
            var nextLink = BuildNextLinkUrl(routeValues, segment.ContinuationToken);

            List<Tuple<TeamMemberEntity, UserInfo>> tuples = new List<Tuple<TeamMemberEntity, UserInfo>>();
            foreach (var member in segment)
            {
                var user = await UserManagement.GetUserByIdAsync(member.UserId, cancellationToken);
                tuples.Add(Tuple.Create(member, user));
            }
            return Ok(ResponseBuilder.BuildResourceList<TeamMemberEntity, UserInfo, TeamMember, TeamMemberList>(
                    tuples,
                    ResponseBuilder.BuildTeamMember,
                    nextLink));
        }
        #endregion

        #region ListAssignmentsByTeam
        /// <summary>
        /// List paginated award assignments of an team.
        /// </summary>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="teamId" example="d1e40c38-cc2a-445f-9eab-60c253256c57">unique Guid of the team. Auto-generated on server side.</param>
        /// <returns>the response contains a list of award assginments and a nextLink if there are more results.</returns>
        /// <response code="200">Success. The response describes a list of award assignments.</response>
        [HttpGet]
        [ProducesResponseType(typeof(AwardAssignmentList), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 404)]
        [Route("hackathon/{hackathonName}/team/{teamId}/assignments")]
        public async Task<object> ListAssignmentsByTeam(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required, Guid] string teamId,
            [FromQuery] Pagination pagination,
            CancellationToken cancellationToken)
        {
            // validate hackathon
            var hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackathonName.ToLower());
            var options = new ValidateHackathonOptions
            {
                HackathonName = hackathonName,
                WritableRequired = false,
            };
            if (await ValidateHackathon(hackathon, options) == false)
            {
                return options.ValidateResult;
            }

            // Validate team
            var teamEntity = await TeamManagement.GetTeamByIdAsync(hackathonName.ToLower(), teamId, cancellationToken);
            var teamValidateOptions = new ValidateTeamOptions
            {
            };
            if (await ValidateTeam(teamEntity, teamValidateOptions) == false)
            {
                return teamValidateOptions.ValidateResult;
            }


            // query
            var assignmentQueryOptions = new AwardAssignmentQueryOptions
            {
                TableContinuationToken = pagination.ToContinuationToken(),
                Top = pagination.top,
                TeamId = teamId,
                QueryType = AwardAssignmentQueryType.Team,
            };
            var assignments = await AwardManagement.ListPaginatedAssignmentsAsync(hackathonName.ToLower(), assignmentQueryOptions, cancellationToken);
            var routeValues = new RouteValueDictionary();
            if (pagination.top.HasValue)
            {
                routeValues.Add(nameof(pagination.top), pagination.top.Value);
            }
            var nextLink = BuildNextLinkUrl(routeValues, assignmentQueryOptions.Next);

            // build resp
            var creator = await UserManagement.GetUserByIdAsync(teamEntity.CreatorId, cancellationToken);
            var team = ResponseBuilder.BuildTeam(teamEntity, creator);
            var resp = await ResponseBuilder.BuildResourceListAsync<AwardAssignmentEntity, AwardAssignment, AwardAssignmentList>(
                assignments,
                (assignment, ct) => Task.FromResult(ResponseBuilder.BuildAwardAssignment(assignment, team, null)),
                nextLink);

            return Ok(resp);
        }
        #endregion

        #region CreateTeamWork
        /// <summary>
        /// Create a new team work
        /// </summary>
        /// <param name="parameter"></param>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="teamId" example="d1e40c38-cc2a-445f-9eab-60c253256c57">unique Guid of the team. Auto-generated on server side.</param>
        /// <returns>The work</returns>
        /// <response code="200">Success. The response describes a team work.</response>
        [HttpPut]
        [ProducesResponseType(typeof(TeamWork), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 404, 412)]
        [Route("hackathon/{hackathonName}/team/{teamId}/work")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.TeamMember)]
        public async Task<object> CreateTeamWork(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required, Guid] string teamId,
            [FromBody] TeamWork parameter,
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
            var team = await TeamManagement.GetTeamByIdAsync(hackathonName.ToLower(), teamId, cancellationToken);
            var teamMember = await TeamManagement.GetTeamMemberAsync(hackathonName.ToLower(), CurrentUserId, cancellationToken);
            var teamMemberValidateOption = new ValidateTeamMemberOptions
            {
                TeamId = teamId,
                UserId = CurrentUserId,
                ApprovedMemberRequired = true,
            };
            if (await ValidateTeamMember(team, teamMember, teamMemberValidateOption, cancellationToken) == false)
            {
                return teamMemberValidateOption.ValidateResult;
            }

            // check work count
            bool canCreate = await WorkManagement.CanCreateTeamWorkAsync(hackathonName.ToLower(), teamId, cancellationToken);
            if (!canCreate)
            {
                return PreconditionFailed(Resources.TeamWork_TooMany);
            }

            // create team work
            parameter.hackathonName = hackathonName.ToLower();
            parameter.teamId = teamId;
            var teamWorkEntity = await WorkManagement.CreateTeamWorkAsync(parameter, cancellationToken);
            return Ok(ResponseBuilder.BuildTeamWork(teamWorkEntity));
        }
        #endregion

        #region UpdateTeamWork
        /// <summary>
        /// Update an existing team work
        /// </summary>
        /// <param name="parameter"></param>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="teamId" example="d1e40c38-cc2a-445f-9eab-60c253256c57">unique Guid of the team. Auto-generated on server side.</param>
        /// <param name="workId" example="c85e65ef-fd5e-4539-a1f8-bafb7e4f9d74">unique Guid of the work. Auto-generated on server side.</param>
        /// <returns>The work</returns>
        /// <response code="200">Success. The response describes a team work.</response>
        [HttpPatch]
        [ProducesResponseType(typeof(TeamWork), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 404)]
        [Route("hackathon/{hackathonName}/team/{teamId}/work/{workId}")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.TeamMember)]
        public async Task<object> UpdateTeamWork(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required, Guid] string teamId,
            [FromRoute, Required, Guid] string workId,
            [FromBody] TeamWork parameter,
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
            var team = await TeamManagement.GetTeamByIdAsync(hackathonName.ToLower(), teamId, cancellationToken);
            var teamMember = await TeamManagement.GetTeamMemberAsync(hackathonName.ToLower(), CurrentUserId, cancellationToken);
            var teamMemberValidateOption = new ValidateTeamMemberOptions
            {
                TeamId = teamId,
                UserId = CurrentUserId,
                ApprovedMemberRequired = true,
            };
            if (await ValidateTeamMember(team, teamMember, teamMemberValidateOption, cancellationToken) == false)
            {
                return teamMemberValidateOption.ValidateResult;
            }

            // create team work
            var teamWorkEntity = await WorkManagement.GetTeamWorkAsync(hackathonName.ToLower(), workId, cancellationToken);
            if (teamWorkEntity == null)
            {
                return NotFound(Resources.TeamWork_NotFound);
            }
            teamWorkEntity = await WorkManagement.UpdateTeamWorkAsync(teamWorkEntity, parameter, cancellationToken);
            return Ok(ResponseBuilder.BuildTeamWork(teamWorkEntity));
        }
        #endregion

        #region GetTeamWork
        /// <summary>
        /// Query a team work.
        /// </summary>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="teamId" example="d1e40c38-cc2a-445f-9eab-60c253256c57">unique Guid of the team. Auto-generated on server side.</param>
        /// <param name="workId" example="c85e65ef-fd5e-4539-a1f8-bafb7e4f9d74">unique Guid of the work. Auto-generated on server side.</param>
        /// <returns>The work</returns>
        /// <response code="200">Success. The response describes a team work.</response>
        [HttpGet]
        [ProducesResponseType(typeof(TeamWork), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 404)]
        [Route("hackathon/{hackathonName}/team/{teamId}/work/{workId}")]
        public async Task<object> GetTeamWork(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required, Guid] string teamId,
            [FromRoute, Required, Guid] string workId,
            CancellationToken cancellationToken)
        {
            // validate hackathon
            var hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackathonName.ToLower(), cancellationToken);
            var options = new ValidateHackathonOptions
            {
                HackathonName = hackathonName,
                OnlineRequired = true,
                WritableRequired = false,
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

            // get team work
            var teamWorkEntity = await WorkManagement.GetTeamWorkAsync(hackathonName.ToLower(), workId, cancellationToken);
            if (teamWorkEntity == null)
            {
                return NotFound(Resources.TeamWork_NotFound);
            }
            return Ok(ResponseBuilder.BuildTeamWork(teamWorkEntity));
        }
        #endregion

        #region ListWorksByTeam
        /// <summary>
        /// List paginated works of an team.
        /// </summary>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="teamId" example="d1e40c38-cc2a-445f-9eab-60c253256c57">unique Guid of the team. Auto-generated on server side.</param>
        /// <returns>the response contains a list of award assginments and a nextLink if there are more results.</returns>
        /// <response code="200">Success. The response describes a list of works.</response>
        [HttpGet]
        [ProducesResponseType(typeof(TeamWorkList), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 404)]
        [Route("hackathon/{hackathonName}/team/{teamId}/works")]
        public async Task<object> ListWorksByTeam(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required, Guid] string teamId,
            [FromQuery] Pagination pagination,
            CancellationToken cancellationToken)
        {
            // validate hackathon
            var hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackathonName.ToLower());
            var options = new ValidateHackathonOptions
            {
                HackathonName = hackathonName,
                WritableRequired = false,
            };
            if (await ValidateHackathon(hackathon, options) == false)
            {
                return options.ValidateResult;
            }

            // Validate team
            var teamEntity = await TeamManagement.GetTeamByIdAsync(hackathonName.ToLower(), teamId, cancellationToken);
            var teamValidateOptions = new ValidateTeamOptions
            {
            };
            if (await ValidateTeam(teamEntity, teamValidateOptions) == false)
            {
                return teamValidateOptions.ValidateResult;
            }


            // query
            var teamWorkQueryOptions = new TeamWorkQueryOptions
            {
                TableContinuationToken = pagination.ToContinuationToken(),
                Top = pagination.top,
            };
            var assignments = await WorkManagement.ListPaginatedWorksAsync(hackathonName.ToLower(), teamId.ToLower(), teamWorkQueryOptions, cancellationToken);
            var routeValues = new RouteValueDictionary();
            if (pagination.top.HasValue)
            {
                routeValues.Add(nameof(pagination.top), pagination.top.Value);
            }
            var nextLink = BuildNextLinkUrl(routeValues, teamWorkQueryOptions.Next);

            // build resp
            var resp = ResponseBuilder.BuildResourceList<TeamWorkEntity, TeamWork, TeamWorkList>(
                assignments,
                ResponseBuilder.BuildTeamWork,
                nextLink);

            return Ok(resp);
        }
        #endregion

        #region DeleteTeamWork
        /// <summary>
        /// Delete an team work by workId
        /// </summary>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="teamId" example="d1e40c38-cc2a-445f-9eab-60c253256c57">unique Guid of the team. Auto-generated on server side.</param>
        /// <param name="workId" example="c85e65ef-fd5e-4539-a1f8-bafb7e4f9d74">unique Guid of the work. Auto-generated on server side.</param>
        /// <response code="204">Deleted. </response>
        [HttpDelete]
        [SwaggerErrorResponse(400, 404)]
        [Route("hackathon/{hackathonName}/team/{teamId}/work/{workId}")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.TeamMember)]
        public async Task<object> DeleteTeamWork(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
           [FromRoute, Required, Guid] string teamId,
            [FromRoute, Required, Guid] string workId,
            CancellationToken cancellationToken)
        {
            // validate hackathon
            var hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackathonName.ToLower(), cancellationToken);
            var options = new ValidateHackathonOptions
            {
                HackathonName = hackathonName,
                HackathonOpenRequired = true,
                OnlineRequired = true,
            };
            if (await ValidateHackathon(hackathon, options, cancellationToken) == false)
            {
                return options.ValidateResult;
            }

            // Validate team and member
            var team = await TeamManagement.GetTeamByIdAsync(hackathonName.ToLower(), teamId, cancellationToken);
            var teamMember = await TeamManagement.GetTeamMemberAsync(hackathonName.ToLower(), CurrentUserId, cancellationToken);
            var teamMemberValidateOption = new ValidateTeamMemberOptions
            {
                TeamId = teamId,
                UserId = CurrentUserId,
                ApprovedMemberRequired = true,
            };
            if (await ValidateTeamMember(team, teamMember, teamMemberValidateOption, cancellationToken) == false)
            {
                return teamMemberValidateOption.ValidateResult;
            }

            // Delete work
            var work = await WorkManagement.GetTeamWorkAsync(hackathonName.ToLower(), workId, cancellationToken);
            if (work == null)
            {
                return NoContent();
            }
            await WorkManagement.DeleteTeamWorkAsync(hackathonName.ToLower(), workId, cancellationToken);
            return NoContent();
        }
        #endregion
    }
}
