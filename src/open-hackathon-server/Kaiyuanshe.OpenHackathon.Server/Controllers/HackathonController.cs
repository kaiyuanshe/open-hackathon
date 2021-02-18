using Kaiyuanshe.OpenHackathon.Server.Auth;
using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.ResponseBuilder;
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

        public IHackathonManagement HackathonManager { get; set; }

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
            var entities = await HackathonManager.SearchHackathonAsync(null, cancellationToken);
            return Ok(ResponseBuilder.BuildHackathonList(entities));
        }

        /// <summary>
        /// Create or update hackathon. 
        /// If hackathon with the {name} exists, will retrive update it accordingly.
        /// Else create a new hackathon.
        /// </summary>
        /// <param name="parameter" example="foo"></param>
        /// <returns></returns>
        /// <response code="200">Success. The response describes a hackathon.</response>
        /// <response code="400">Bad Reqeuest. The response indicates the client request is not valid.</response>
        /// <response code="403">Forbidden. The response indicates the user doesn't have proper access.</response>
        [HttpPut]
        [ProducesResponseType(typeof(Hackathon), StatusCodes.Status200OK)]
        [Route("hackathon/{name}")]
        [Authorize]
        public async Task<object> CreateOrUpdate(
            [FromRoute, Required, RegularExpression("^[A-Za-z0-9]{1,100}$")] string name,
            [FromBody] Hackathon parameter,
            CancellationToken cancellationToken)
        {
            if (!ModelState.IsValid)
            {
                return BadRequest(ErrorResponse.BadArgument("Invalid request", details: GetErrors()));
            }

            parameter.Name = name;
            var entity = await HackathonManager.GetHackathonEntityByNameAsync(name, cancellationToken);
            if (entity != null)
            {
                // make sure only Admin of this hackathon can update it
                var authorizationResult = await AuthorizationService.AuthorizeAsync(User, entity, AuthConstant.Policy.HackathonAdministrator);
                if (!authorizationResult.Succeeded)
                {
                    return StatusCode(403, ErrorResponse.Forbidden("access denied. Please contact the administrator of the hackathon."));
                }

                var updated = await HackathonManager.UpdateHackathonAsync(parameter, cancellationToken);
                return Ok(ResponseBuilder.BuildHackathon(updated));
            }
            else
            {
                var created = await HackathonManager.CreateHackathonAsync(parameter, cancellationToken);
                return Ok(ResponseBuilder.BuildHackathon(created));
            }
        }
    }
}
