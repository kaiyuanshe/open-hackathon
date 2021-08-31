using Kaiyuanshe.OpenHackathon.Server.Auth;
using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Kaiyuanshe.OpenHackathon.Server.Swagger;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Routing;
using System.ComponentModel.DataAnnotations;
using System.Text.RegularExpressions;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Controllers
{
    public class HackathonController : HackathonControllerBase
    {
        #region ListHackathon
        /// <summary>
        /// List paginated online hackathons.
        /// </summary>
        /// <param name="cancellationToken"></param>
        /// <param name="search">keyword to search in name, display name or details. Do case-insensitive substring match only.</param>
        /// <param name="orderby">order by. Default to createdAt.</param>
        /// <param name="listType">type of list. Default to online. 
        /// online: list hackathons in online status only; 
        /// admin: list hackathons in any status where current user has admin access.
        /// enrolled: list enrolled hackathons.
        /// fresh: hackathons that are about to start.
        /// </param>
        /// <returns>A list of hackathon.</returns>
        /// <response code="200">Success. The response describes a list of hackathon and a nullable link to query more results.</response>
        [HttpGet]
        [ProducesResponseType(typeof(HackathonList), 200)]
        [Route("hackathons")]
        public async Task<object> ListHackathon(
            [FromQuery] Pagination pagination,
            [FromQuery] string search,
            [FromQuery] HackathonOrderBy? orderby,
            [FromQuery] HackathonListType? listType,
            CancellationToken cancellationToken)
        {
            // check login if list by admin
            if (listType == HackathonListType.admin)
            {
                var authorizationResult = await AuthorizationService.AuthorizeAsync(User, null, AuthConstant.PolicyForSwagger.LoginUser);
                if (!authorizationResult.Succeeded)
                {
                    return Unauthorized(Resources.Auth_Unauthorized);
                }
            }

            var hackathonQueryOptions = new HackathonQueryOptions
            {
                TableContinuationToken = pagination.ToContinuationToken(),
                OrderBy = orderby,
                Search = search,
                ListType = listType,
                Top = pagination.top
            };
            var entities = await HackathonManagement.ListPaginatedHackathonsAsync(User, hackathonQueryOptions, cancellationToken);
            var entityWithRoles = await HackathonManagement.ListHackathonRolesAsync(entities, User, cancellationToken);

            var routeValues = new RouteValueDictionary();
            if (pagination.top.HasValue)
            {
                routeValues.Add(nameof(pagination.top), pagination.top.Value);
            }
            routeValues.Add(nameof(search), search);
            if (orderby.HasValue)
            {
                routeValues.Add(nameof(orderby), orderby.Value);
            }
            if (listType.HasValue)
            {
                routeValues.Add(nameof(listType), listType.Value);
            }
            var nextLink = BuildNextLinkUrl(routeValues, hackathonQueryOptions.Next);

            return Ok(ResponseBuilder.BuildResourceList<HackathonEntity, HackathonRoles, Hackathon, HackathonList>(
                    entityWithRoles, ResponseBuilder.BuildHackathon, nextLink));
        }
        #endregion

        #region CheckNameAvailability
        /// <summary>
        /// Check the name availability
        /// </summary>
        /// <param name="parameter">parameter including the name to check</param>
        /// <param name="cancellationToken"></param>
        /// <returns>availability and a reason if not available.</returns>
        [HttpPost]
        [Route("hackathon/checkNameAvailability")]
        [SwaggerErrorResponse(400, 401)]
        [ProducesResponseType(typeof(NameAvailability), StatusCodes.Status200OK)]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.LoginUser)]
        public async Task<object> CheckNameAvailability(
            [FromBody, Required] NameAvailability parameter,
            CancellationToken cancellationToken)
        {
            if (!Regex.IsMatch(parameter.name, ModelConstants.HackathonNamePattern))
            {
                return parameter.Invalid(Resources.Hackathon_Name_Invalid);
            }

            var entity = await HackathonManagement.GetHackathonEntityByNameAsync(parameter.name.ToLower(), cancellationToken);
            if (entity != null)
            {
                return parameter.AlreadyExists(Resources.Hackathon_Name_Taken);
            }

            return parameter.OK();
        }
        #endregion

        #region CreateOrUpdate
        /// <summary>
        /// Create or update hackathon. 
        /// If hackathon with the {hackathonName} exists, will retrive update it accordingly(must be admin of the hackathon).
        /// Else create a new hackathon.
        /// </summary>
        /// <param name="parameter"></param>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <returns></returns>
        /// <response code="200">Success. The response describes a hackathon.</response>
        [HttpPut]
        [ProducesResponseType(typeof(Hackathon), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 403, 412)]
        [Route("hackathon/{hackathonName}")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.HackathonAdministrator)]
        public async Task<object> CreateOrUpdate(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromBody] Hackathon parameter,
            CancellationToken cancellationToken)
        {
            string nameLowercase = hackathonName.ToLower();
            parameter.name = nameLowercase;
            var entity = await HackathonManagement.GetHackathonEntityByNameAsync(nameLowercase, cancellationToken);
            if (entity != null)
            {
                return await UpdateInternal(entity, parameter, cancellationToken);
            }
            else
            {
                var canCreate = await HackathonManagement.CanCreateHackathonAsync(User, cancellationToken);
                if (!canCreate)
                {
                    return PreconditionFailed(Resources.Hackathon_CreateTooMany);
                }

                parameter.creatorId = CurrentUserId;
                var created = await HackathonManagement.CreateHackathonAsync(parameter, cancellationToken);
                var roles = await HackathonManagement.GetHackathonRolesAsync(created, User, cancellationToken);
                return Ok(ResponseBuilder.BuildHackathon(created, roles));
            }
        }
        #endregion

        #region Update

        /// <summary>
        /// Update hackathon. Caller must be adminstrator of the hackathon. 
        /// </summary>
        /// <param name="parameter"></param>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <returns></returns>
        /// <response code="200">Success. The response describes a hackathon.</response>
        [HttpPatch]
        [ProducesResponseType(typeof(Hackathon), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 403, 404)]
        [Route("hackathon/{hackathonName}")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.HackathonAdministrator)]
        public async Task<object> Update(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromBody] Hackathon parameter,
            CancellationToken cancellationToken)
        {
            string nameLowercase = hackathonName.ToLower();
            parameter.name = nameLowercase;
            var entity = await HackathonManagement.GetHackathonEntityByNameAsync(nameLowercase, cancellationToken);
            return await UpdateInternal(entity, parameter, cancellationToken);
        }

        private async Task<object> UpdateInternal(HackathonEntity entity, Hackathon parameter, CancellationToken cancellationToken)
        {
            var options = new ValidateHackathonOptions
            {
                HackAdminRequird = true,
                HackathonName = parameter.name,
            };
            if (await ValidateHackathon(entity, options, cancellationToken) == false)
            {
                return options.ValidateResult;
            }

            var updated = await HackathonManagement.UpdateHackathonAsync(parameter, cancellationToken);
            var roles = await HackathonManagement.GetHackathonRolesAsync(entity, User, cancellationToken);
            return Ok(ResponseBuilder.BuildHackathon(updated, roles));
        }
        #endregion

        #region Get
        /// <summary>
        /// Query a hackathon by name.
        /// </summary>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <returns></returns>
        /// <response code="200">Success. The response describes a hackathon.</response>
        [HttpGet]
        [ProducesResponseType(typeof(Hackathon), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 404)]
        [Route("hackathon/{hackathonName}")]
        public async Task<object> Get(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            CancellationToken cancellationToken)
        {
            var entity = await HackathonManagement.GetHackathonEntityByNameAsync(hackathonName.ToLower(), cancellationToken);
            if (entity == null)
            {
                return NotFound(string.Format(Resources.Hackathon_NotFound, hackathonName));
            }

            var role = await HackathonManagement.GetHackathonRolesAsync(entity, User, cancellationToken);
            if (!entity.IsOnline() && (role == null || !role.isAdmin))
            {
                return NotFound(string.Format(Resources.Hackathon_NotFound, hackathonName));
            }

            return Ok(ResponseBuilder.BuildHackathon(entity, role));
        }
        #endregion

        #region Delete
        /// <summary>
        /// Delete a hackathon by name. The hackathon is marked as Deleted, the record becomes invisible.
        /// </summary>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <returns></returns>
        /// <response code="204">Success. The response indicates the hackathon is deleted.</response>
        [HttpDelete]
        [Route("hackathon/{hackathonName}")]
        [SwaggerErrorResponse(400, 403)]
        [Authorize(AuthConstant.Policy.PlatformAdministrator)]
        public async Task<object> Delete(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            CancellationToken cancellationToken)
        {
            var entity = await HackathonManagement.GetHackathonEntityByNameAsync(hackathonName.ToLower());
            if (entity == null || entity.Status == HackathonStatus.offline)
            {
                return NoContent();
            }

            await HackathonManagement.UpdateHackathonStatusAsync(entity, HackathonStatus.offline, cancellationToken);
            return NoContent();
        }
        #endregion

        #region RequestPublish
        /// <summary>
        /// Send an request to publish a draft hackathon. The hackathon will go online after the request approved.
        /// </summary>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="cancellationToken"></param>
        /// <returns>the hackathon</returns>
        [HttpPost]
        [Route("hackathon/{hackathonName}/requestPublish")]
        [SwaggerErrorResponse(400, 404, 412)]
        [ProducesResponseType(typeof(Hackathon), StatusCodes.Status200OK)]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.HackathonAdministrator)]
        public async Task<object> RequestPublish(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            CancellationToken cancellationToken)
        {
            // validate hackathon
            HackathonEntity hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackathonName.ToLower(), cancellationToken);
            var options = new ValidateHackathonOptions
            {
                HackathonName = hackathonName,
                UserId = CurrentUserId,
                HackAdminRequird = true,
                NotDeletedRequired = true,
            };
            if (await ValidateHackathon(hackathon, options) == false)
            {
                return options.ValidateResult;
            }
            if (hackathon.Status == HackathonStatus.online)
            {
                return PreconditionFailed(string.Format(Resources.Hackathon_AlreadyOnline, hackathonName));
            }

            // update status
            hackathon = await HackathonManagement.UpdateHackathonStatusAsync(hackathon, HackathonStatus.pendingApproval, cancellationToken);

            // resp
            var roles = await HackathonManagement.GetHackathonRolesAsync(hackathon, User, cancellationToken);
            return Ok(ResponseBuilder.BuildHackathon(hackathon, roles));
        }
        #endregion

        #region Publish
        /// <summary>
        /// Publish a hackathon. The hackathon will go online and become visible to everyone.
        /// </summary>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="cancellationToken"></param>
        /// <returns>the hackathon</returns>
        [HttpPost]
        [Route("hackathon/{hackathonName}/publish")]
        [SwaggerErrorResponse(400, 404, 412)]
        [ProducesResponseType(typeof(Hackathon), StatusCodes.Status200OK)]
        [Authorize(Policy = AuthConstant.Policy.PlatformAdministrator)]
        public async Task<object> Publish(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            CancellationToken cancellationToken)
        {
            // validate hackathon
            HackathonEntity hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackathonName.ToLower(), cancellationToken);
            var options = new ValidateHackathonOptions
            {
                HackathonName = hackathonName,
                UserId = CurrentUserId,
            };
            if (await ValidateHackathon(hackathon, options) == false)
            {
                return options.ValidateResult;
            }

            // update status
            hackathon = await HackathonManagement.UpdateHackathonStatusAsync(hackathon, HackathonStatus.online, cancellationToken);

            // resp
            var roles = await HackathonManagement.GetHackathonRolesAsync(hackathon, User, cancellationToken);
            return Ok(ResponseBuilder.BuildHackathon(hackathon, roles));
        }
        #endregion

        #region UpdateReadOnly
        /// <summary>
        /// Mark a hackathon as Readnly or not Readonly. 
        /// A readonly hackathon cannot be updated. Team, Award, Rating etc are all readonly.
        /// </summary>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="cancellationToken"></param>
        /// <returns>the hackathon</returns>
        [HttpPost]
        [Route("hackathon/{hackathonName}/updateReadonly")]
        [SwaggerErrorResponse(400, 404)]
        [ProducesResponseType(typeof(Hackathon), StatusCodes.Status200OK)]
        [Authorize(Policy = AuthConstant.Policy.PlatformAdministrator)]
        public async Task<object> UpdateReadonly(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromQuery, Required] bool readOnly,
            CancellationToken cancellationToken)
        {
            // validate hackathon
            HackathonEntity hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackathonName.ToLower(), cancellationToken);
            var options = new ValidateHackathonOptions
            {
                WritableRequired = false,
                HackathonName = hackathonName,
                UserId = CurrentUserId,
            };
            if (await ValidateHackathon(hackathon, options) == false)
            {
                return options.ValidateResult;
            }

            // update status
            hackathon = await HackathonManagement.UpdateHackathonReadOnlyAsync(hackathon, readOnly, cancellationToken);

            // resp
            var roles = await HackathonManagement.GetHackathonRolesAsync(hackathon, User, cancellationToken);
            return Ok(ResponseBuilder.BuildHackathon(hackathon, roles));
        }
        #endregion
    }
}
