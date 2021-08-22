using Kaiyuanshe.OpenHackathon.Server.Cache;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Storage;
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
    public interface IRatingManagement
    {
        Task<bool> CanCreateRatingKindAsync(string hackathonName, CancellationToken cancellationToken);
        Task<RatingKindEntity> CreateRatingKindAsync(RatingKind parameter, CancellationToken cancellationToken);
        Task<RatingKindEntity> UpdateRatingKindAsync(RatingKindEntity existing, RatingKind parameter, CancellationToken cancellationToken);
        Task<RatingKindEntity> GetCachedRatingKindAsync(string hackathonName, string kindId, CancellationToken cancellationToken);
        Task<RatingKindEntity> GetRatingKindAsync(string hackathonName, string kindId, CancellationToken cancellationToken);
        Task<IEnumerable<RatingKindEntity>> ListPaginatedRatingKindsAsync(string hackathonName, RatingKindQueryOptions options, CancellationToken cancellationToken = default);
        Task DeleteRatingKindAsync(string hackathonName, string kindId, CancellationToken cancellationToken);
        Task<RatingEntity> CreateRatingAsync(Rating parameter, CancellationToken cancellationToken);
        Task<RatingEntity> UpdateRatingAsync(RatingEntity existing, Rating parameter, CancellationToken cancellationToken);
        Task<RatingEntity> GetRatingAsync(string hackathonName, string judgeId, string teamId, string kindId, CancellationToken cancellationToken);
        Task<RatingEntity> GetRatingAsync(string hackathonName, string ratingId, CancellationToken cancellationToken);
        Task<bool> IsRatingCountGreaterThanZero(string hackathonName, RatingQueryOptions options, CancellationToken cancellationToken);
        Task<TableQuerySegment<RatingEntity>> ListPaginatedRatingsAsync(string hackathonName, RatingQueryOptions options, CancellationToken cancellationToken = default);
        Task DeleteRatingAsync(string hackathonName, string ratingId, CancellationToken cancellationToken);
    }

    public class RatingManagement : ManagementClientBase, IRatingManagement
    {
        static readonly int MaxRatingKindCount = 100;

        private readonly ILogger Logger;

        public RatingManagement(ILogger<RatingManagement> logger)
        {
            Logger = logger;
        }

        #region Cache
        private string CacheKeyRatingKinds(string hackathonName)
        {
            return CacheKeys.GetCacheKey(CacheEntryType.RatingKind, hackathonName);
        }

        private void InvalidateCachedRatingKinds(string hackathonName)
        {
            Cache.Remove(CacheKeyRatingKinds(hackathonName));
        }

        #endregion

        #region Task<bool> CanCreateRatingKindAsync(string hackathonName, CancellationToken cancellationToken)
        public async Task<bool> CanCreateRatingKindAsync(string hackathonName, CancellationToken cancellationToken)
        {
            var kinds = await ListRatingKindsAsync(hackathonName, cancellationToken);
            return kinds.Count() < MaxRatingKindCount;
        }
        #endregion

        #region Task<RatingKindEntity> CreateRatingKindAsync(RatingKind parameter, CancellationToken cancellationToken);
        public async Task<RatingKindEntity> CreateRatingKindAsync(RatingKind parameter, CancellationToken cancellationToken)
        {
            if (parameter == null)
                return null;

            var entity = new RatingKindEntity
            {
                PartitionKey = parameter.hackathonName,
                RowKey = Guid.NewGuid().ToString(),
                CreatedAt = DateTime.UtcNow,
                Description = parameter.description,
                MaximumScore = parameter.maximumScore.GetValueOrDefault(10),
                Name = parameter.name,
            };
            await StorageContext.RatingKindTable.InsertAsync(entity, cancellationToken);
            InvalidateCachedRatingKinds(parameter.hackathonName);
            return entity;
        }
        #endregion

        #region Task<RatingKindEntity> UpdateRatingKindAsync(RatingKindEntity existing, RatingKind parameter, CancellationToken cancellationToken)
        public async Task<RatingKindEntity> UpdateRatingKindAsync(RatingKindEntity existing, RatingKind parameter, CancellationToken cancellationToken)
        {
            if (existing == null || parameter == null)
                return existing;

            existing.Name = parameter.name ?? existing.Name;
            existing.Description = parameter.description ?? existing.Description;
            existing.MaximumScore = parameter.maximumScore.GetValueOrDefault(existing.MaximumScore);
            await StorageContext.RatingKindTable.MergeAsync(existing, cancellationToken);
            InvalidateCachedRatingKinds(existing.HackathonName);

            return existing;
        }
        #endregion

        #region Task<RatingKindEntity> GetCachedRatingKindAsync(string hackathonName, string kindId, CancellationToken cancellationToken);
        public async Task<RatingKindEntity> GetCachedRatingKindAsync(string hackathonName, string kindId, CancellationToken cancellationToken)
        {
            var allKinds = await ListRatingKindsAsync(hackathonName, cancellationToken);
            return allKinds.FirstOrDefault(k => k.Id == kindId);
        }
        #endregion

        #region Task<RatingKindEntity> GetRatingKindAsync(string hackathonName, string kindId, CancellationToken cancellationToken)
        public async Task<RatingKindEntity> GetRatingKindAsync(string hackathonName, string kindId, CancellationToken cancellationToken)
        {
            if (string.IsNullOrWhiteSpace(hackathonName) || string.IsNullOrWhiteSpace(kindId))
                return null;

            return await StorageContext.RatingKindTable.RetrieveAsync(hackathonName, kindId, cancellationToken);
        }
        #endregion

        #region Task<IEnumerable<RatingKindEntity>> ListPaginatedRatingKindsAsync(string hackathonName, RatingKindQueryOptions options, CancellationToken cancellationToken = default)
        private async Task<IEnumerable<RatingKindEntity>> ListRatingKindsAsync(string hackathonName, CancellationToken cancellationToken = default)
        {
            string cacheKey = CacheKeyRatingKinds(hackathonName);
            return await Cache.GetOrAddAsync(
                cacheKey,
                TimeSpan.FromHours(4),
                (ct) => StorageContext.RatingKindTable.ListRatingKindsAsync(hackathonName, ct),
                true,
                cancellationToken);
        }

        public async Task<IEnumerable<RatingKindEntity>> ListPaginatedRatingKindsAsync(string hackathonName, RatingKindQueryOptions options, CancellationToken cancellationToken = default)
        {
            var allKinds = await ListRatingKindsAsync(hackathonName, cancellationToken);

            // paging
            int np = 0;
            int.TryParse(options.TableContinuationToken?.NextPartitionKey, out np);
            int top = options.Top.GetValueOrDefault(100);
            var kinds = allKinds.OrderByDescending(a => a.CreatedAt)
                .Skip(np)
                .Take(top);

            // next paging
            options.Next = null;
            if (np + top < allKinds.Count())
            {
                options.Next = new TableContinuationToken
                {
                    NextPartitionKey = (np + top).ToString(),
                    NextRowKey = (np + top).ToString(),
                };
            }

            return kinds;
        }
        #endregion

        #region Task DeleteJudgeAsync(string hackathonName, string kindId, CancellationToken cancellationToken)
        public async Task DeleteRatingKindAsync(string hackathonName, string kindId, CancellationToken cancellationToken)
        {
            if (string.IsNullOrWhiteSpace(hackathonName) || string.IsNullOrWhiteSpace(kindId))
                return;

            await StorageContext.RatingKindTable.DeleteAsync(hackathonName, kindId, cancellationToken);
            InvalidateCachedRatingKinds(hackathonName);
        }
        #endregion

        #region Task<RatingEntity> CreateRatingAsync(Rating parameter, CancellationToken cancellationToken);
        public async Task<RatingEntity> CreateRatingAsync(Rating parameter, CancellationToken cancellationToken)
        {
            var ratingEntity = new RatingEntity
            {
                PartitionKey = parameter.hackathonName,
                RowKey = GenerateRatingEntityRowKey(parameter.judgeId, parameter.teamId, parameter.ratingKindId),
                CreatedAt = DateTime.UtcNow,
                Description = parameter.description,
                JudgeId = parameter.judgeId,
                RatingKindId = parameter.ratingKindId,
                Score = parameter.score.GetValueOrDefault(0),
                TeamId = parameter.teamId,
            };

            await StorageContext.RatingTable.InsertOrMergeAsync(ratingEntity, cancellationToken);
            return ratingEntity;
        }
        #endregion

        #region Task<RatingEntity> UpdateRatingAsync(RatingEntity exiting, Rating parameter, CancellationToken cancellationToken)
        public async Task<RatingEntity> UpdateRatingAsync(RatingEntity existing, Rating parameter, CancellationToken cancellationToken)
        {
            if (existing == null || parameter == null)
                return existing;

            existing.Score = parameter.score.GetValueOrDefault(existing.Score);
            existing.Description = parameter.description ?? existing.Description;

            await StorageContext.RatingTable.MergeAsync(existing, cancellationToken);
            return existing;
        }
        #endregion

        #region Task<RatingEntity> GetRatingAsync(string hackathonName, string judgeId, string teamId, string kindId, CancellationToken cancellationToken)
        public async Task<RatingEntity> GetRatingAsync(string hackathonName, string judgeId, string teamId, string kindId, CancellationToken cancellationToken)
        {
            if (string.IsNullOrWhiteSpace(hackathonName)
                || string.IsNullOrWhiteSpace(judgeId)
                || string.IsNullOrWhiteSpace(teamId)
                || string.IsNullOrWhiteSpace(kindId))
                return null;

            var rowKey = GenerateRatingEntityRowKey(judgeId, teamId, kindId);
            return await StorageContext.RatingTable.RetrieveAsync(hackathonName, rowKey, cancellationToken);
        }
        #endregion

        #region Task<RatingEntity> GetRatingAsync(string hackathonName, string ratingId, CancellationToken cancellationToken);
        public async Task<RatingEntity> GetRatingAsync(string hackathonName, string ratingId, CancellationToken cancellationToken)
        {
            if (string.IsNullOrWhiteSpace(hackathonName) || string.IsNullOrWhiteSpace(ratingId))
                return null;

            return await StorageContext.RatingTable.RetrieveAsync(hackathonName, ratingId, cancellationToken);
        }
        #endregion

        #region Task<bool> IsRatingCountGreaterThanZero(string hackathonName, RatingQueryOptions options, CancellationToken cancellationToken);
        public async Task<bool> IsRatingCountGreaterThanZero(string hackathonName, RatingQueryOptions options, CancellationToken cancellationToken)
        {
            var filter = TableQuery.GenerateFilterCondition(nameof(RatingEntity.PartitionKey), QueryComparisons.Equal, hackathonName);
            if (!string.IsNullOrWhiteSpace(options.JudgeId))
            {
                filter = TableQueryHelper.And(filter,
                    TableQuery.GenerateFilterCondition(nameof(RatingEntity.JudgeId), QueryComparisons.Equal, options.JudgeId));
            }
            if (!string.IsNullOrWhiteSpace(options.RatingKindId))
            {
                filter = TableQueryHelper.And(filter,
                    TableQuery.GenerateFilterCondition(nameof(RatingEntity.RatingKindId), QueryComparisons.Equal, options.RatingKindId));
            }
            if (!string.IsNullOrWhiteSpace(options.TeamId))
            {
                filter = TableQueryHelper.And(filter,
                    TableQuery.GenerateFilterCondition(nameof(RatingEntity.TeamId), QueryComparisons.Equal, options.TeamId));
            }

            TableQuery<RatingEntity> query = new TableQuery<RatingEntity>()
                .Where(filter)
                .Select(new[] { nameof(RatingEntity.RowKey) })
                .Take(1);

            TableContinuationToken continuationToken = null;
            var segment = await StorageContext.RatingTable.ExecuteQuerySegmentedAsync(query, continuationToken, cancellationToken);
            return segment.Count() > 0;
        }
        #endregion

        #region Task<TableQuerySegment<RatingEntity>> ListPaginatedRatingsAsync(string hackathonName, RatingQueryOptions options, CancellationToken cancellationToken = default)
        public async Task<TableQuerySegment<RatingEntity>> ListPaginatedRatingsAsync(string hackathonName, RatingQueryOptions options, CancellationToken cancellationToken = default)
        {
            var filter = TableQuery.GenerateFilterCondition(nameof(RatingEntity.PartitionKey), QueryComparisons.Equal, hackathonName);
            if (!string.IsNullOrWhiteSpace(options.JudgeId))
            {
                filter = TableQueryHelper.And(filter,
                    TableQuery.GenerateFilterCondition(nameof(RatingEntity.JudgeId), QueryComparisons.Equal, options.JudgeId));
            }
            if (!string.IsNullOrWhiteSpace(options.RatingKindId))
            {
                filter = TableQueryHelper.And(filter,
                    TableQuery.GenerateFilterCondition(nameof(RatingEntity.RatingKindId), QueryComparisons.Equal, options.RatingKindId));
            }
            if (!string.IsNullOrWhiteSpace(options.TeamId))
            {
                filter = TableQueryHelper.And(filter,
                    TableQuery.GenerateFilterCondition(nameof(RatingEntity.TeamId), QueryComparisons.Equal, options.TeamId));
            }

            int top = 100;
            if (options != null && options.Top.HasValue && options.Top.Value > 0)
            {
                top = options.Top.Value;
            }
            TableQuery<RatingEntity> query = new TableQuery<RatingEntity>()
                .Where(filter)
                .Take(top);

            TableContinuationToken continuationToken = options?.TableContinuationToken;
            return await StorageContext.RatingTable.ExecuteQuerySegmentedAsync(query, continuationToken, cancellationToken);
        }
        #endregion

        #region Task DeleteRatingAsync(string hackathonName, string ratingId, CancellationToken cancellationToken)
        public async Task DeleteRatingAsync(string hackathonName, string ratingId, CancellationToken cancellationToken)
        {
            if (string.IsNullOrWhiteSpace(hackathonName) || string.IsNullOrWhiteSpace(ratingId))
                return;

            await StorageContext.RatingTable.DeleteAsync(hackathonName, ratingId, cancellationToken);
        }
        #endregion

        private string GenerateRatingEntityRowKey(string judgeId, string teamId, string kindId)
        {
            string input = $"{judgeId}-{teamId}-{kindId}".ToLower();
            var guid = DigestHelper.String2Guid(input);
            return guid.ToString();
        }
    }
}
