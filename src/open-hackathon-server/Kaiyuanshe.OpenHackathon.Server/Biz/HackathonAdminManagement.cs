using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.Extensions.Logging;
using System;
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
    }

    public class HackathonAdminManagement : ManagementClientBase, IHackathonAdminManagement
    {
        private readonly ILogger logger;

        public HackathonAdminManagement(ILogger<HackathonAdminManagement> logger)
        {
            this.logger = logger;
        }

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
            return entity;
        }
        #endregion
    }
}
