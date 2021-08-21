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
    public class AwardController : HackathonControllerBase
    {
        #region CreateAward
        /// <summary>
        /// Create a new award
        /// </summary>
        /// <param name="parameter"></param>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <returns>The award</returns>
        /// <response code="200">Success. The response describes an award.</response>
        [HttpPut]
        [ProducesResponseType(typeof(Award), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 404, 412)]
        [Route("hackathon/{hackathonName}/award")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.HackathonAdministrator)]
        public async Task<object> CreateAward(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromBody] Award parameter,
            CancellationToken cancellationToken)
        {
            // validate hackathon
            var hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackathonName.ToLower(), cancellationToken);
            var options = new ValidateHackathonOptions
            {
                HackAdminRequird = true,
                HackathonName = hackathonName,
            };
            if (await ValidateHackathon(hackathon, options, cancellationToken) == false)
            {
                return options.ValidateResult;
            }

            // check award count
            bool canCreate = await AwardManagement.CanCreateNewAward(hackathonName.ToLower(), cancellationToken);
            if (!canCreate)
            {
                return PreconditionFailed(Resources.Award_TooMany);
            }

            // create award
            parameter.hackathonName = hackathonName.ToLower();
            var awardEntity = await AwardManagement.CreateAwardAsync(hackathonName.ToLower(), parameter, cancellationToken);
            return Ok(ResponseBuilder.BuildAward(awardEntity));
        }
        #endregion

        #region GetAward
        /// <summary>
        /// Query an award
        /// </summary>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="awardId" example="c877c675-4c97-4deb-9e48-97d079fa4b72">unique Guid of the award. Auto-generated on server side.</param>
        /// <returns>The award</returns>
        /// <response code="200">Success. The response describes an award.</response>
        [HttpGet]
        [ProducesResponseType(typeof(Award), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 404)]
        [Route("hackathon/{hackathonName}/award/{awardId}")]
        public async Task<object> GetAward(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required, Guid] string awardId,
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

            // get award
            var award = await AwardManagement.GetAwardByIdAsync(hackathonName.ToLower(), awardId, cancellationToken);
            var awardOptions = new ValidateAwardOptions { };
            if (await ValidateAward(award, awardOptions, cancellationToken) == false)
            {
                return awardOptions.ValidateResult;
            }
            return Ok(ResponseBuilder.BuildAward(award));
        }
        #endregion

        #region UpdateAward
        /// <summary>
        /// Update an award
        /// </summary>
        /// <param name="parameter"></param>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="awardId" example="c877c675-4c97-4deb-9e48-97d079fa4b72">unique Guid of the award. Auto-generated on server side.</param>
        /// <returns>The award</returns>
        /// <response code="200">Success. The response describes an award.</response>
        [HttpPatch]
        [ProducesResponseType(typeof(Award), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 403, 404, 412)]
        [Route("hackathon/{hackathonName}/award/{awardId}")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.HackathonAdministrator)]
        public async Task<object> UpdateAward(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required, Guid] string awardId,
            [FromBody] Award parameter,
            CancellationToken cancellationToken)
        {
            // validate hackathon
            var hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackathonName.ToLower(), cancellationToken);
            var options = new ValidateHackathonOptions
            {
                HackAdminRequird = true,
                HackathonName = hackathonName,
            };
            if (await ValidateHackathon(hackathon, options, cancellationToken) == false)
            {
                return options.ValidateResult;
            }

            // validate award
            var award = await AwardManagement.GetAwardByIdAsync(hackathonName.ToLower(), awardId, cancellationToken);
            var awardOptions = new ValidateAwardOptions
            {
                TargetChangableRequired = true,
                NewTarget = parameter.target.GetValueOrDefault(award.Target),
            };
            if (await ValidateAward(award, awardOptions, cancellationToken) == false)
            {
                return awardOptions.ValidateResult;
            }

            // update award
            var updated = await AwardManagement.UpdateAwardAsync(award, parameter, cancellationToken);
            return Ok(ResponseBuilder.BuildAward(updated));
        }
        #endregion

        #region ListAwards
        /// <summary>
        /// List paginated awards of a hackathon.
        /// </summary>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <returns>the response contains a list of awards and a nextLink if there are more results.</returns>
        /// <response code="200">Success.</response>
        [HttpGet]
        [ProducesResponseType(typeof(AwardList), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 404)]
        [Route("hackathon/{hackathonName}/awards")]
        public async Task<object> ListAwards(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
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

            // query
            var awardQueryOptions = new AwardQueryOptions
            {
                TableContinuationToken = pagination.ToContinuationToken(),
                Top = pagination.top
            };
            var awards = await AwardManagement.ListPaginatedAwardsAsync(hackathonName.ToLower(), awardQueryOptions, cancellationToken);
            var routeValues = new RouteValueDictionary();
            if (pagination.top.HasValue)
            {
                routeValues.Add(nameof(pagination.top), pagination.top.Value);
            }
            var nextLink = BuildNextLinkUrl(routeValues, awardQueryOptions.Next);
            return Ok(ResponseBuilder.BuildResourceList<AwardEntity, Award, AwardList>(
                    awards,
                    ResponseBuilder.BuildAward,
                    nextLink));
        }
        #endregion

        #region DeleteAward
        /// <summary>
        /// Delete an award
        /// </summary>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="awardId" example="c877c675-4c97-4deb-9e48-97d079fa4b72">unique Guid of the award. Auto-generated on server side.</param>
        /// <response code="204">Success. The response indicates that an award is deleted.</response>
        [HttpDelete]
        [SwaggerErrorResponse(400, 404)]
        [Route("hackathon/{hackathonName}/award/{awardId}")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.HackathonAdministrator)]
        public async Task<object> DeleteAward(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required, Guid] string awardId,
            CancellationToken cancellationToken)
        {
            // validate hackathon
            var hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackathonName.ToLower(), cancellationToken);
            var options = new ValidateHackathonOptions
            {
                HackAdminRequird = true,
                HackathonName = hackathonName,
            };
            if (await ValidateHackathon(hackathon, options, cancellationToken) == false)
            {
                return options.ValidateResult;
            }

            // get award
            var award = await AwardManagement.GetAwardByIdAsync(hackathonName.ToLower(), awardId, cancellationToken);
            if (award == null)
            {
                return NoContent();
            }
            var assignmentCount = await AwardManagement.GetAssignmentCountAsync(hackathonName.ToLower(), award.Id, cancellationToken);
            if (assignmentCount > 0)
            {
                return PreconditionFailed(Resources.Award_CannotDeleteAssigned);
            }

            // delete award
            await AwardManagement.DeleteAwardAsync(award, cancellationToken);
            return NoContent();
        }
        #endregion

        #region BuildAwardAssignment
        private async Task<AwardAssignment> BuildAwardAssignment(
            AwardAssignmentEntity awardAssignmentEntity,
            AwardEntity awardEntity,
            CancellationToken cancellationToken)
        {
            switch (awardEntity.Target)
            {
                case AwardTarget.team:
                    var teamEntity = await TeamManagement.GetTeamByIdAsync(awardEntity.HackathonName, awardAssignmentEntity.AssigneeId, cancellationToken);
                    var teamCreator = await UserManagement.GetUserByIdAsync(teamEntity.CreatorId, cancellationToken);
                    var team = ResponseBuilder.BuildTeam(teamEntity, teamCreator);
                    return ResponseBuilder.BuildAwardAssignment(awardAssignmentEntity, team, null);
                case AwardTarget.individual:
                    var user = await UserManagement.GetUserByIdAsync(awardAssignmentEntity.AssigneeId, cancellationToken);
                    return ResponseBuilder.BuildAwardAssignment(awardAssignmentEntity, null, user);
                default:
                    return null;
            }
        }
        #endregion

        #region CreateAwardAssignment
        /// <summary>
        /// Assign an award
        /// </summary>
        /// <param name="parameter"></param>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="awardId" example="c877c675-4c97-4deb-9e48-97d079fa4b72">unique Guid of the award. Auto-generated on server side.</param>
        /// <returns>The award assignment</returns>
        /// <response code="200">Success. The response describes an award assignment.</response>
        [HttpPut]
        [ProducesResponseType(typeof(AwardAssignment), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 403, 404, 412)]
        [Route("hackathon/{hackathonName}/award/{awardId}/assignment")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.HackathonAdministrator)]
        public async Task<object> CreateAwardAssignment(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required, Guid] string awardId,
            [FromBody, HttpPutPolicy] AwardAssignment parameter,
            CancellationToken cancellationToken)
        {
            // validate hackathon
            var hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackathonName.ToLower(), cancellationToken);
            var options = new ValidateHackathonOptions
            {
                HackAdminRequird = true,
                HackathonName = hackathonName,
            };
            if (await ValidateHackathon(hackathon, options, cancellationToken) == false)
            {
                return options.ValidateResult;
            }

            // validate award
            var awardEntity = await AwardManagement.GetAwardByIdAsync(hackathonName.ToLower(), awardId, cancellationToken);
            var validateAwardOptions = new ValidateAwardOptions
            {
                QuantityCheckRequired = true,
                AssigneeExistRequired = true,
                AssigneeId = parameter.assigneeId,
            };
            if (await ValidateAward(awardEntity, validateAwardOptions, cancellationToken) == false)
            {
                return validateAwardOptions.ValidateResult;
            }

            parameter.hackathonName = hackathonName.ToLower();
            parameter.awardId = awardId;
            var assignment = await AwardManagement.CreateOrUpdateAssignmentAsync(parameter, cancellationToken);
            return Ok(await BuildAwardAssignment(assignment, awardEntity, cancellationToken));
        }
        #endregion

        #region UpdateAwardAssignment
        /// <summary>
        /// Update an award assignment. AwardId and AssigneeId will not be updated. 
        /// </summary>
        /// <param name="parameter"></param>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="awardId" example="c877c675-4c97-4deb-9e48-97d079fa4b72">unique Guid of the award. Auto-generated on server side.</param>
        /// <param name="assignmentId" example="270d61b3-c676-403b-b582-cc38dfe122e4">unique Guid of the assignment. Auto-generated on server side.</param>
        /// <returns>The award assignment</returns>
        /// <response code="200">Success. The response describes an award assignment.</response>
        [HttpPatch]
        [ProducesResponseType(typeof(AwardAssignment), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 403, 404)]
        [Route("hackathon/{hackathonName}/award/{awardId}/assignment/{assignmentId}")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.HackathonAdministrator)]
        public async Task<object> UpdateAwardAssignment(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required, Guid] string awardId,
            [FromRoute, Required, Guid] string assignmentId,
            [FromBody] AwardAssignment parameter,
            CancellationToken cancellationToken)
        {
            // validate hackathon
            var hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackathonName.ToLower(), cancellationToken);
            var options = new ValidateHackathonOptions
            {
                HackAdminRequird = true,
                HackathonName = hackathonName,
            };
            if (await ValidateHackathon(hackathon, options, cancellationToken) == false)
            {
                return options.ValidateResult;
            }

            // validate award
            var awardEntity = await AwardManagement.GetAwardByIdAsync(hackathonName.ToLower(), awardId, cancellationToken);
            var validateAwardOptions = new ValidateAwardOptions
            {
            };
            if (await ValidateAward(awardEntity, validateAwardOptions, cancellationToken) == false)
            {
                return validateAwardOptions.ValidateResult;
            }

            // update assignment
            var assignment = await AwardManagement.GetAssignmentAsync(hackathonName.ToLower(), assignmentId, cancellationToken);
            if (assignment == null)
            {
                return NotFound(Resources.AwardAssignment_NotFound);
            }
            assignment = await AwardManagement.UpdateAssignmentAsync(assignment, parameter, cancellationToken);
            return Ok(await BuildAwardAssignment(assignment, awardEntity, cancellationToken));
        }
        #endregion

        #region GetAwardAssignment
        /// <summary>
        /// Get an award assignment by assignmentId
        /// </summary>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="awardId" example="c877c675-4c97-4deb-9e48-97d079fa4b72">unique Guid of the award. Auto-generated on server side.</param>
        /// <param name="assignmentId" example="270d61b3-c676-403b-b582-cc38dfe122e4">unique Guid of the assignment. Auto-generated on server side.</param>
        /// <returns>The award assignment</returns>
        /// <response code="200">Success. The response describes an award assignment.</response>
        [HttpGet]
        [ProducesResponseType(typeof(AwardAssignment), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 404)]
        [Route("hackathon/{hackathonName}/award/{awardId}/assignment/{assignmentId}")]
        public async Task<object> GetAwardAssignment(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required, Guid] string awardId,
            [FromRoute, Required, Guid] string assignmentId,
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

            // validate award
            var awardEntity = await AwardManagement.GetAwardByIdAsync(hackathonName.ToLower(), awardId, cancellationToken);
            var validateAwardOptions = new ValidateAwardOptions
            {
            };
            if (await ValidateAward(awardEntity, validateAwardOptions, cancellationToken) == false)
            {
                return validateAwardOptions.ValidateResult;
            }

            // update assignment
            var assignment = await AwardManagement.GetAssignmentAsync(hackathonName.ToLower(), assignmentId, cancellationToken);
            if (assignment == null)
            {
                return NotFound(Resources.AwardAssignment_NotFound);
            }
            return Ok(await BuildAwardAssignment(assignment, awardEntity, cancellationToken));
        }
        #endregion

        #region ListAssignmentsByAward
        /// <summary>
        /// List paginated assignments of an award.
        /// </summary>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="awardId" example="c877c675-4c97-4deb-9e48-97d079fa4b72">unique Guid of the award. Auto-generated on server side.</param>
        /// <returns>the response contains a list of award assginments and a nextLink if there are more results.</returns>
        /// <response code="200">Success. The response describes a list of award assignments.</response>
        [HttpGet]
        [ProducesResponseType(typeof(AwardAssignmentList), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 404)]
        [Route("hackathon/{hackathonName}/award/{awardId}/assignments")]
        public async Task<object> ListAssignmentsByAward(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required, Guid] string awardId,
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

            // validate award
            var awardEntity = await AwardManagement.GetAwardByIdAsync(hackathonName.ToLower(), awardId, cancellationToken);
            var validateAwardOptions = new ValidateAwardOptions
            {
            };
            if (await ValidateAward(awardEntity, validateAwardOptions, cancellationToken) == false)
            {
                return validateAwardOptions.ValidateResult;
            }

            // query
            var assignmentQueryOptions = new AwardAssignmentQueryOptions
            {
                TableContinuationToken = pagination.ToContinuationToken(),
                Top = pagination.top,
                AwardId = awardId,
                QueryType = AwardAssignmentQueryType.Award,
            };
            var assignments = await AwardManagement.ListPaginatedAssignmentsAsync(hackathonName.ToLower(), assignmentQueryOptions, cancellationToken);
            var routeValues = new RouteValueDictionary();
            if (pagination.top.HasValue)
            {
                routeValues.Add(nameof(pagination.top), pagination.top.Value);
            }
            var nextLink = BuildNextLinkUrl(routeValues, assignmentQueryOptions.Next);

            var resp = await ResponseBuilder.BuildResourceListAsync<AwardAssignmentEntity, AwardAssignment, AwardAssignmentList>(
                assignments,
                (assignment, ct) => BuildAwardAssignment(assignment, awardEntity, ct),
                nextLink);

            return Ok(resp);
        }
        #endregion

        #region ListAssignmentsByHackathon
        /// <summary>
        /// List paginated assignments of a hackathon.
        /// </summary>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <returns>the response contains a list of award assginments and a nextLink if there are more results.</returns>
        /// <response code="200">Success. The response describes a list of award assignments.</response>
        [HttpGet]
        [ProducesResponseType(typeof(AwardAssignmentList), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 404)]
        [Route("hackathon/{hackathonName}/assignments")]
        public async Task<object> ListAssignmentsByHackathon(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
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

            // query
            var assignmentQueryOptions = new AwardAssignmentQueryOptions
            {
                TableContinuationToken = pagination.ToContinuationToken(),
                Top = pagination.top,
                QueryType = AwardAssignmentQueryType.Hackathon,
            };
            var assignments = await AwardManagement.ListPaginatedAssignmentsAsync(hackathonName.ToLower(), assignmentQueryOptions, cancellationToken);
            var routeValues = new RouteValueDictionary();
            if (pagination.top.HasValue)
            {
                routeValues.Add(nameof(pagination.top), pagination.top.Value);
            }
            var nextLink = BuildNextLinkUrl(routeValues, assignmentQueryOptions.Next);

            var awards = await AwardManagement.ListAwardsAsync(hackathonName.ToLower(), cancellationToken);
            var resp = await ResponseBuilder.BuildResourceListAsync<AwardAssignmentEntity, AwardAssignment, AwardAssignmentList>(
                assignments,
                async (assignment, ct) =>
                {
                    var awardEntity = awards.SingleOrDefault(a => a.Id == assignment.AwardId);
                    if (awardEntity == null)
                        return null;
                    return await BuildAwardAssignment(assignment, awardEntity, ct);
                },
                nextLink);

            return Ok(resp);
        }
        #endregion

        #region DeleteAwardAssignment
        /// <summary>
        /// Delete an award assignment by assignmentId
        /// </summary>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="awardId" example="c877c675-4c97-4deb-9e48-97d079fa4b72">unique Guid of the award. Auto-generated on server side.</param>
        /// <param name="assignmentId" example="270d61b3-c676-403b-b582-cc38dfe122e4">unique Guid of the assignment. Auto-generated on server side.</param>
        /// <returns>The award assignment</returns>
        /// <response code="204">Deleted. </response>
        [HttpDelete]
        [SwaggerErrorResponse(400, 404)]
        [Route("hackathon/{hackathonName}/award/{awardId}/assignment/{assignmentId}")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.HackathonAdministrator)]
        public async Task<object> DeleteAwardAssignment(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required, Guid] string awardId,
            [FromRoute, Required, Guid] string assignmentId,
            CancellationToken cancellationToken)
        {
            // validate hackathon
            var hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackathonName.ToLower(), cancellationToken);
            var options = new ValidateHackathonOptions
            {
                HackathonName = hackathonName,
                HackAdminRequird = true,
            };
            if (await ValidateHackathon(hackathon, options, cancellationToken) == false)
            {
                return options.ValidateResult;
            }

            // validate award
            var awardEntity = await AwardManagement.GetAwardByIdAsync(hackathonName.ToLower(), awardId, cancellationToken);
            var validateAwardOptions = new ValidateAwardOptions
            {
            };
            if (await ValidateAward(awardEntity, validateAwardOptions, cancellationToken) == false)
            {
                return validateAwardOptions.ValidateResult;
            }

            // Delete assignment
            var assignment = await AwardManagement.GetAssignmentAsync(hackathonName.ToLower(), assignmentId, cancellationToken);
            if (assignment == null)
            {
                return NoContent();
            }
            await AwardManagement.DeleteAssignmentAsync(hackathonName.ToLower(), assignmentId, cancellationToken);
            return NoContent();
        }
        #endregion
    }
}
