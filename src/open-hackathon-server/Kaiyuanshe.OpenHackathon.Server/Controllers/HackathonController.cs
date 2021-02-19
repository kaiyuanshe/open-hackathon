using Kaiyuanshe.OpenHackathon.Server.Auth;
using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.ResponseBuilder;
using Kaiyuanshe.OpenHackathon.Server.Storage;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using System.ComponentModel.DataAnnotations;
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
        [Authorize]
        public async Task<object> ListHackathon(CancellationToken cancellationToken)
        {
            var entities = await HackathonManagement.SearchHackathonAsync(null, cancellationToken);
            return Ok(ResponseBuilder.BuildHackathonList(entities));
        }

        /// <summary>
        /// Create or update hackathon. 
        /// If hackathon with the {name} exists, will retrive update it accordingly(must be admin of the hackathon).
        /// Else create a new hackathon.
        /// </summary>
        /// <param name="parameter"></param>
        /// <param name="name" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <returns></returns>
        /// <response code="200">Success. The response describes a hackathon.</response>
        /// <response code="400">Bad Reqeuest. The response indicates the client request is not valid.</response>
        /// <response code="403">Forbidden. The response indicates the user doesn't have proper access.</response>
        [HttpPut]
        [ProducesResponseType(typeof(Hackathon), StatusCodes.Status200OK)]
        [Route("hackathon/{name}")]
        [Authorize]
        public async Task<object> CreateOrUpdate(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string name,
            [FromBody] Hackathon parameter)
        {
            if (!ModelState.IsValid)
            {
                return BadRequest(ErrorResponse.BadArgument(Resources.Request_Invalid, details: GetErrors()));
            }
            string nameLowercase = name.ToLower();
            parameter.Name = nameLowercase;
            var entity = await HackathonManagement.GetHackathonEntityByNameAsync(nameLowercase);
            if (entity != null)
            {
                // make sure only Admin of this hackathon can update it
                var authorizationResult = await AuthorizationService.AuthorizeAsync(User, entity, AuthConstant.Policy.HackathonAdministrator);
                if (!authorizationResult.Succeeded)
                {
                    return StatusCode(403, ErrorResponse.Forbidden(Resources.Request_Forbidden_HackAdmin));
                }

                var updated = await HackathonManagement.UpdateHackathonAsync(parameter);
                return Ok(ResponseBuilder.BuildHackathon(updated));
            }
            else
            {
                parameter.CreatorId = CurrentUserId;
                var created = await HackathonManagement.CreateHackathonAsync(parameter);
                return Ok(ResponseBuilder.BuildHackathon(created));
            }
        }

        /// <summary>
        /// Query a hackathon by name.
        /// </summary>
        /// <param name="name" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <returns></returns>
        /// <response code="200">Success. The response describes a hackathon.</response>
        /// <response code="400">Bad Reqeuest. The response indicates the client request is not valid.</response>
        /// <response code="404">Not Found. The response indicates the hackathon with specified name doesn't exist.</response>
        [HttpGet]
        [ProducesResponseType(typeof(Hackathon), StatusCodes.Status200OK)]
        [Route("hackathon/{name}")]
        public async Task<object> Get(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string name)
        {
            if (!ModelState.IsValid)
            {
                return BadRequest(ErrorResponse.BadArgument(Resources.Request_Invalid, details: GetErrors()));
            }

            var entity = await HackathonManagement.GetHackathonEntityByNameAsync(name.ToLower());
            if (entity == null)
            {
                return NotFound(ErrorResponse.NotFound(string.Format(Resources.Hackathon_NotFound, name)));
            }

            return Ok(ResponseBuilder.BuildHackathon(entity));
        }
    }
}
