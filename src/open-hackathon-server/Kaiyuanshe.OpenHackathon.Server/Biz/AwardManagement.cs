using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Biz
{
    public interface IAwardManagement
    {
        /// <summary>
        /// Get a Award by Id
        /// </summary>
        /// <param name="hackathonName">name of hackathon</param>
        /// <param name="awardId">unique id of the award</param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<AwardEntity> GeAwardByIdAsync(string hackathonName, string awardId, CancellationToken cancellationToken = default);
    }


    public class AwardManagement : ManagementClientBase, IAwardManagement
    {
        private readonly ILogger Logger;

        public AwardManagement(ILogger<AwardManagement> logger)
        {
            Logger = logger;
        }

        public async Task<AwardEntity> GeAwardByIdAsync(string hackathonName, string awardId, CancellationToken cancellationToken = default)
        {
            if (string.IsNullOrWhiteSpace(hackathonName) || string.IsNullOrWhiteSpace(awardId))
                return null;

            return await StorageContext.AwardTable.RetrieveAsync(hackathonName.ToLower(), awardId, cancellationToken);
        }
    }
}
