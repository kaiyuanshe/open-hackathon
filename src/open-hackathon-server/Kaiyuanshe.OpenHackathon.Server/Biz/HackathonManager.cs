using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Storage;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Biz
{
    public interface IHackathonManager
    {
        /// <summary>
        /// Search hackathon
        /// </summary>
        /// <param name="options"></param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<IEnumerable<HackathonEntity>> SearchHackathonAsync(HackathonSearchOptions options, CancellationToken cancellationToken = default);
        /// <summary>
        /// Get Hackathon By Id. Return null if not found.
        /// </summary>
        /// <param name="id"></param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<HackathonEntity> GetHackathonEntityByIdAsync(string id, CancellationToken cancellationToken);
    }

    public class HackathonManager : IHackathonManager
    {
        public IStorageContext StorageContext { get; set; }

        public async Task<IEnumerable<HackathonEntity>> SearchHackathonAsync(HackathonSearchOptions options, CancellationToken cancellationToken = default)
        {
            var entities = new List<HackathonEntity>();
            await StorageContext.HackathonTable.ExecuteQuerySegmentedAsync(null, (segment) =>
            {
                entities.AddRange(segment);
            }, cancellationToken);

            return entities;
        }

        public async Task<HackathonEntity> GetHackathonEntityByIdAsync(string id, CancellationToken cancellationToken = default)
        {
            var entity = await StorageContext.HackathonTable.RetrieveAsync(id, string.Empty, cancellationToken);
            return entity;
        }
    }

    public class HackathonSearchOptions
    {

    }
}
