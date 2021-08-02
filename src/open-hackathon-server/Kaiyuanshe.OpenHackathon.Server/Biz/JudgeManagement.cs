using Kaiyuanshe.OpenHackathon.Server.Cache;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.Extensions.Logging;
using System;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Biz
{
    public interface IJudgeManagement
    {
        Task<JudgeEntity> CreateJudgeAsync(Judge parameter, CancellationToken cancellationToken);
        Task<JudgeEntity> GetJudgeAsync(string hackathonName, string userId, CancellationToken cancellationToken);
    }

    public class JudgeManagement : ManagementClientBase, IJudgeManagement
    {
        private readonly ILogger Logger;

        public JudgeManagement(ILogger<JudgeManagement> logger)
        {
            Logger = logger;
        }

        #region Cache
        private string CacheKeyByHackathon(string hackathonName)
        {
            return CacheKeys.GetCacheKey(CacheEntryType.Judge, hackathonName);
        }

        private void InvalidateCachedJudges(string hackathonName)
        {
            Cache.Remove(CacheKeyByHackathon(hackathonName));
        }
        #endregion

        #region Task<JudgeEntity> CreateJudgeAsync(Judge parameter, CancellationToken cancellationToken);
        public async Task<JudgeEntity> CreateJudgeAsync(Judge parameter, CancellationToken cancellationToken)
        {
            JudgeEntity entity = new JudgeEntity
            {
                PartitionKey = parameter.hackathonName,
                RowKey = parameter.userId,
                CreatedAt = DateTime.UtcNow,
                Description = parameter.description,
            };
            await StorageContext.JudgeTable.InsertOrReplaceAsync(entity, cancellationToken);
            InvalidateCachedJudges(parameter.hackathonName);
            return entity;
        }
        #endregion

        #region Task<JudgeEntity> GetJudgeAsync(string hackathonName, string userId, CancellationToken cancellationToken);
        public async Task<JudgeEntity> GetJudgeAsync(string hackathonName, string userId, CancellationToken cancellationToken)
        {
            if (string.IsNullOrWhiteSpace(hackathonName) || string.IsNullOrWhiteSpace(userId))
                return null;

            return await StorageContext.JudgeTable.RetrieveAsync(hackathonName, userId, cancellationToken);
        }
        #endregion
    }
}
