using Kaiyuanshe.OpenHackathon.Server.Auth;
using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.ResponseBuilder;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Kaiyuanshe.OpenHackathon.Server.Swagger;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using System.ComponentModel.DataAnnotations;
using System.Text.RegularExpressions;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Controllers
{
    public class HackathonController : HackathonControllerBase
    {
        public IResponseBuilder ResponseBuilder { get; set; }

        public IHackathonManagement HackathonManagement { get; set; }

        /// <summary>
        /// List hackathons.
        /// </summary>
        /// <param name="cancellationToken"></param>
        /// <returns>A list of hackathon.</returns>
        /// <response code="200">Success. The response describes a list of hackathon.</response>
        [HttpGet]
        [ProducesResponseType(typeof(HackathonList), 200)]
        [Route("hackathons")]
        public async Task<object> ListHackathon(CancellationToken cancellationToken)
        {
            var entities = await HackathonManagement.SearchHackathonAsync(null, cancellationToken);
            return Ok(ResponseBuilder.BuildHackathonList(entities));
        }

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
        [SwaggerErrorResponse(400, 403)]
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
                parameter.creatorId = CurrentUserId;
                var created = await HackathonManagement.CreateHackathonAsync(parameter, cancellationToken);
                var roles = await HackathonManagement.GetHackathonRolesAsync(nameLowercase, User, cancellationToken);
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
        #endregion

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
            var roles = await HackathonManagement.GetHackathonRolesAsync(parameter.name, User, cancellationToken);
            return Ok(ResponseBuilder.BuildHackathon(updated, roles));
        }

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

            var role = await HackathonManagement.GetHackathonRolesAsync(hackathonName.ToLower(), User, cancellationToken);
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
    }
}
