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
    public interface IRatingManagement
    {
        Task<RatingKindEntity> CreateRatingKindAsync(RatingKind parameter, CancellationToken cancellationToken);
        Task<RatingKindEntity> UpdateRatingKindAsync(RatingKindEntity existing, RatingKind parameter, CancellationToken cancellationToken);
        Task<RatingKindEntity> GetRatingKindAsync(string hackathonName, string kindId, CancellationToken cancellationToken);
        Task<IEnumerable<RatingKindEntity>> ListPaginatedRatingKindsAsync(string hackathonName, RatingKindQueryOptions options, CancellationToken cancellationToken = default);
    }

    public class RatingManagement : ManagementClientBase, IRatingManagement
    {
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
                MaximumRating = parameter.maximumRating.GetValueOrDefault(10),
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
            existing.MaximumRating = parameter.maximumRating.GetValueOrDefault(existing.MaximumRating);
            await StorageContext.RatingKindTable.MergeAsync(existing, cancellationToken);
            InvalidateCachedRatingKinds(existing.HackathonName);

            return existing;
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
    }
}
