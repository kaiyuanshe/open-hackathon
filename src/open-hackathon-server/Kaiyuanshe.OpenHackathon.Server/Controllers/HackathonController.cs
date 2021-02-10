using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Filters;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.ResponseBuilder;
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

        public IHackathonManager HackathonManager { get; set; }

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
        [HttpPut]
        [ProducesResponseType(typeof(Hackathon), StatusCodes.Status200OK)]
        [Route("hackathon/{name}")]
        [TokenRequired]
        public async Task<object> CreateOrUpdate(
            [FromRoute, Required, RegularExpression("^[a-z0-9]{1,100}$")] string name,
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
                var updated = await HackathonManager.UpdateHackathonAsync(parameter, cancellationToken);
                return Ok(updated);
            }
            else
            {
                var created = await HackathonManager.CreateHackathonAsync(parameter, cancellationToken);
                return Ok(created);
            }
        }
    }
}
