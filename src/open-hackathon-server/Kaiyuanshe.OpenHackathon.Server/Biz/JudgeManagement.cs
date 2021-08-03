using Kaiyuanshe.OpenHackathon.Server.Cache;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.Extensions.Logging;
using Microsoft.WindowsAzure.Storage.Table;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Biz
{
    public interface IJudgeManagement
    {
        Task<JudgeEntity> CreateJudgeAsync(Judge parameter, CancellationToken cancellationToken);
        Task<JudgeEntity> GetJudgeAsync(string hackathonName, string userId, CancellationToken cancellationToken);
        Task<IEnumerable<JudgeEntity>> ListPaginatedJudgesAsync(string hackathonName, JudgeQueryOptions options, CancellationToken cancellationToken = default);
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

        private async Task<IEnumerable<JudgeEntity>> GetCachedJudges(string hackathonName, CancellationToken cancellationToken)
        {
            string cacheKey = CacheKeyByHackathon(hackathonName);
            return await Cache.GetOrAddAsync(cacheKey, TimeSpan.FromHours(6), (ct) =>
            {
                return StorageContext.JudgeTable.ListByHackathonAsync(hackathonName, ct);
            }, true, cancellationToken);
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

        #region Task<IEnumerable<JudgeEntity>> ListPaginatedJudgesAsync(string hackathonName, JudgeQueryOptions options, CancellationToken cancellationToken = default);
        public async Task<IEnumerable<JudgeEntity>> ListPaginatedJudgesAsync(string hackathonName, JudgeQueryOptions options, CancellationToken cancellationToken = default)
        {
            IEnumerable<JudgeEntity> allJudges = await GetCachedJudges(hackathonName, cancellationToken);

            // paging
            int.TryParse(options.TableContinuationToken?.NextPartitionKey, out int np);
            int top = options.Top.GetValueOrDefault(100);
            var judges = allJudges.OrderByDescending(a => a.CreatedAt).Skip(np).Take(top);

            // next paging
            options.Next = null;
            if (np + top < allJudges.Count())
            {
                options.Next = new TableContinuationToken
                {
                    NextPartitionKey = (np + top).ToString(),
                    NextRowKey = (np + top).ToString(),
                };
            }

            return judges;
        }
        #endregion
    }
}
