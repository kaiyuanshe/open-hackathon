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
        public IStorageContext StorageContext { get; set; }

        [HttpGet]
        [Route("hackathon")]
        public async Task<object> List(CancellationToken cancellationToken)
        {
            var entities = new List<HackathonEntity>();
            await StorageContext.HackathonTable.ExecuteQuerySegmentedAsync(null, (segment) =>
            {
                entities.AddRange(segment);
            }, cancellationToken);

            return Ok(entities);
        }
    }
}
