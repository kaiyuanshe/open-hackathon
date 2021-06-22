using Kaiyuanshe.OpenHackathon.Server.Cache;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Biz
{
    public interface IHackathonAdminManagement
    {
        /// <summary>
        ///  create a new hackathon admin
        /// </summary>
        /// <param name="admin"></param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<HackathonAdminEntity> CreateAdminAsync(HackathonAdmin admin, CancellationToken cancellationToken = default);

        /// <summary>
        /// List all Administrators of a Hackathon. PlatformAdministrator is not included.
        /// </summary>
        /// <param name="hackathonName">name of Hackathon</param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<IEnumerable<HackathonAdminEntity>> ListHackathonAdminAsync(string hackathonName, CancellationToken cancellationToken = default);
    }

    public class HackathonAdminManagement : ManagementClientBase, IHackathonAdminManagement
    {
        private readonly ILogger logger;

        public HackathonAdminManagement(ILogger<HackathonAdminManagement> logger)
        {
            this.logger = logger;
        }

        #region cache

        private void InvalidateAdminCache(string hackathonName)
        {
            string cacheKey = CacheKeys.GetCacheKey(CacheEntryType.HackathonAdmin, hackathonName);
            Cache.Remove(cacheKey);
        }

        #endregion

        #region CreateAdminAsync
        public async Task<HackathonAdminEntity> CreateAdminAsync(HackathonAdmin admin, CancellationToken cancellationToken = default)
        {
            HackathonAdminEntity entity = new HackathonAdminEntity
            {
                PartitionKey = admin.hackathonName,
                RowKey = admin.userId,
                CreatedAt = DateTime.UtcNow,
            };
            await StorageContext.HackathonAdminTable.InsertAsync(entity, cancellationToken);

            InvalidateAdminCache(admin.hackathonName);
            return entity;
        }
        #endregion

        #region ListHackathonAdminAsync
        public async Task<IEnumerable<HackathonAdminEntity>> ListHackathonAdminAsync(string hackathonName, CancellationToken cancellationToken = default)
        {
            string cacheKey = CacheKeys.GetCacheKey(CacheEntryType.HackathonAdmin, hackathonName);
            return await Cache.GetOrAddAsync(cacheKey,
                TimeSpan.FromHours(1),
                (token) =>
                {
                    return StorageContext.HackathonAdminTable.ListByHackathonAsync(hackathonName, token);
                }, true, cancellationToken);
        }
        #endregion
    }
}
