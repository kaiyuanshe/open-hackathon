using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.ResponseBuilder;
using Kaiyuanshe.OpenHackathon.Server.Storage;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.AspNetCore.Mvc;
using System.Collections.Generic;
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
        [ProducesResponseType(typeof(Hackathon[]), 200)]
        [Route("hackathons")]
        public async Task<object> ListHackathon(CancellationToken cancellationToken)
        {
            var entities = await HackathonManager.SearchHackathonAsync(null, cancellationToken);
            return Ok(ResponseBuilder.BuildHackathonList(entities));
        }

        /// <summary>
        /// Create or update hackathon. 
        /// If id is absent, will create a new hackathon. 
        /// If id is not empty, will retrive the hackathon(return 404 if not found) and update accordingly.
        /// </summary>
        /// <param name="parameter"></param>
        /// <returns></returns>
        /// <response code="200">Success. The response describes a hackathon.</response>
        /// <response code="404">Not Found. The response indicates hackathon with specified id doesn't exist.</response>
        [HttpPut]
        [ProducesResponseType(typeof(Hackathon), 200)]
        public async Task<object> CreateOrUpdate(Hackathon parameter, CancellationToken cancellationToken)
        {
            if(!string.IsNullOrEmpty(parameter.Id))
            {
                var entity = await HackathonManager.GetHackathonEntityByIdAsync(parameter.Id, cancellationToken);
                if(entity == null)
                {
                    return NotFound(ErrorResponse.NotFound($"Hackathon with id {parameter.Id} not found."));
                }
                // TO UPDATE
            }
            else
            {
                // TODO create
            }
            return Ok(parameter);
        }
    }
}
