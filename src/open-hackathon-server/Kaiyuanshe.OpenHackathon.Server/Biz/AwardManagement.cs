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
    public interface IAwardManagement
    {
        /// <summary>
        /// Get a Award by Id
        /// </summary>
        Task<AwardEntity> GetAwardByIdAsync(string hackathonName, string awardId, CancellationToken cancellationToken = default);

        Task<bool> CanCreateNewAward(string hackathonName, CancellationToken cancellationToken = default);

        /// <summary>
        /// Create a new Award. No existeance check.
        /// </summary>
        Task<AwardEntity> CreateAwardAsync(string hackathonName, Award award, CancellationToken cancellationToken = default);

        /// <summary>
        /// Update a new Award. No existeance check.
        /// </summary>
        Task<AwardEntity> UpdateAwardAsync(AwardEntity entity, Award award, CancellationToken cancellationToken = default);

        /// <summary>
        /// List awards, internal only
        /// </summary>
        Task<IEnumerable<AwardEntity>> ListAwardsAsync(string hackathonName, CancellationToken cancellationToken = default);

        /// <summary>
        /// List paged awards of hackathon
        /// </summary>
        Task<IEnumerable<AwardEntity>> ListPaginatedAwardsAsync(string hackathonName, AwardQueryOptions options, CancellationToken cancellationToken = default);

        /// <summary>
        /// Delete a new Award. 
        /// </summary>
        Task DeleteAwardAsync(AwardEntity entity, CancellationToken cancellationToken = default);

        /// <summary>
        /// Create or Update Assignment async
        /// </summary>
        Task<AwardAssignmentEntity> CreateOrUpdateAssignmentAsync(AwardAssignment request, CancellationToken cancellationToken = default);

        /// <summary>
        /// Update an asssignment.
        /// </summary>
        Task<AwardAssignmentEntity> UpdateAssignmentAsync(AwardAssignmentEntity existing, AwardAssignment request, CancellationToken cancellationToken = default);

        /// <summary>
        /// Get count of assignment of an award
        /// </summary>
        Task<int> GetAssignmentCountAsync(string hackathonName, string awardId, CancellationToken cancellationToken = default);

        /// <summary>
        /// Get assignment by Id
        /// </summary>
        Task<AwardAssignmentEntity> GetAssignmentAsync(string hackathonName, string assignmentId, CancellationToken cancellationToken = default);

        /// <summary>
        /// List paginated assignments by award
        /// </summary>
        Task<IEnumerable<AwardAssignmentEntity>> ListPaginatedAssignmentsAsync(string hackathonName, AwardAssignmentQueryOptions options, CancellationToken cancellationToken = default);

        /// <summary>
        /// Delete assignment by Id
        /// </summary>
        Task DeleteAssignmentAsync(string hackathonName, string assignmentId, CancellationToken cancellationToken = default);

        /// <summary>
        /// List award assignments by a team
        /// </summary>
        Task<IEnumerable<AwardAssignmentEntity>> ListAssignmentsByTeamAsync(string hackathonName, string teamId, CancellationToken cancellationToken = default);
    }

    public class AwardManagement : ManagementClientBase, IAwardManagement
    {
        static readonly int MaxAwardCount = 100;

        private readonly ILogger Logger;

        public AwardManagement(ILogger<AwardManagement> logger)
        {
            Logger = logger;
        }

        #region Cache
        private string CacheKeyAwards(string hackathonName)
        {
            return CacheKeys.GetCacheKey(CacheEntryType.Award, hackathonName);
        }

        private void InvalidateAwardsCache(string hackathonName)
        {
            Cache.Remove(CacheKeyAwards(hackathonName));
        }

        private async Task<IEnumerable<AwardAssignmentEntity>> ListByAwardAsync(string hackathonName, string awardId, CancellationToken cancellationToken = default)
        {
            string cacheKey = CacheKeys.GetCacheKey(CacheEntryType.AwardAssignment, $"{hackathonName}-{awardId}");
            return await Cache.GetOrAddAsync(cacheKey, TimeSpan.FromSeconds(10), (ct) =>
            {
                return StorageContext.AwardAssignmentTable.ListByAwardAsync(hackathonName, awardId, ct);
            }, false, cancellationToken);
        }

        private async Task<IEnumerable<AwardAssignmentEntity>> ListByHackathonAsync(string hackathonName, CancellationToken cancellationToken = default)
        {
            string cacheKey = CacheKeys.GetCacheKey(CacheEntryType.AwardAssignment, $"{hackathonName}");
            return await Cache.GetOrAddAsync(cacheKey, TimeSpan.FromSeconds(60), (ct) =>
            {
                return StorageContext.AwardAssignmentTable.ListByHackathonAsync(hackathonName, ct);
            }, false, cancellationToken);
        }
        #endregion

        #region Task<bool> CanCreateNewAward(string hackathonName, CancellationToken cancellationToken = default)
        public async Task<bool> CanCreateNewAward(string hackathonName, CancellationToken cancellationToken = default)
        {
            var awards = await ListAwardsAsync(hackathonName, cancellationToken);
            return awards.Count() < MaxAwardCount;
        }
        #endregion

        #region CreateAwardAsync
        public async Task<AwardEntity> CreateAwardAsync(string hackathonName, Award award, CancellationToken cancellationToken = default)
        {
            if (string.IsNullOrWhiteSpace(hackathonName) || award == null)
                return null;

            var awardEnity = new AwardEntity
            {
                PartitionKey = hackathonName.ToLower(),
                RowKey = Guid.NewGuid().ToString(),
                Description = award.description,
                Name = award.name,
                Quantity = award.quantity.GetValueOrDefault(1),
                Target = award.target.GetValueOrDefault(AwardTarget.team),
                Pictures = award.pictures,
                CreatedAt = DateTime.UtcNow,
            };
            await StorageContext.AwardTable.InsertAsync(awardEnity);
            InvalidateAwardsCache(hackathonName);
            return awardEnity;
        }
        #endregion

        #region DeleteAwardAsync
        public async Task DeleteAwardAsync(AwardEntity entity, CancellationToken cancellationToken = default)
        {
            if (entity == null)
                return;

            await StorageContext.AwardTable.DeleteAsync(entity.PartitionKey, entity.RowKey, cancellationToken);
            InvalidateAwardsCache(entity.HackathonName);
        }
        #endregion

        #region GetAwardByIdAsync
        public async Task<AwardEntity> GetAwardByIdAsync(string hackathonName, string awardId, CancellationToken cancellationToken = default)
        {
            if (string.IsNullOrWhiteSpace(hackathonName) || string.IsNullOrWhiteSpace(awardId))
                return null;

            return await StorageContext.AwardTable.RetrieveAsync(hackathonName.ToLower(), awardId, cancellationToken);
        }
        #endregion

        #region ListAwardsAsync
        public async Task<IEnumerable<AwardEntity>> ListAwardsAsync(string hackathonName, CancellationToken cancellationToken = default)
        {
            return await Cache.GetOrAddAsync(
                CacheKeyAwards(hackathonName),
                TimeSpan.FromHours(4),
                (ct) => StorageContext.AwardTable.ListAllAwardsAsync(hackathonName, ct),
                true,
                cancellationToken);
        }
        #endregion

        #region ListPaginatedAwardsAsync
        public async Task<IEnumerable<AwardEntity>> ListPaginatedAwardsAsync(string hackathonName, AwardQueryOptions options, CancellationToken cancellationToken = default)
        {
            var allAwards = await ListAwardsAsync(hackathonName, cancellationToken);

            // paging
            int np = 0;
            int.TryParse(options.TableContinuationToken?.NextPartitionKey, out np);
            int top = options.Top.GetValueOrDefault(100);
            var awards = allAwards.OrderByDescending(a => a.CreatedAt)
                .Skip(np)
                .Take(top);

            // next paging
            options.Next = null;
            if (np + top < allAwards.Count())
            {
                options.Next = new TableContinuationToken
                {
                    NextPartitionKey = (np + top).ToString(),
                    NextRowKey = (np + top).ToString(),
                };
            }

            return awards;
        }
        #endregion

        #region UpdateAwardAsync
        public async Task<AwardEntity> UpdateAwardAsync(AwardEntity entity, Award award, CancellationToken cancellationToken = default)
        {
            if (entity == null || award == null)
                return entity;

            if (!string.IsNullOrEmpty(award.description)) entity.Description = award.description;
            if (!string.IsNullOrEmpty(award.name)) entity.Name = award.name;
            if (award.pictures != null) entity.Pictures = award.pictures;
            if (award.quantity.HasValue) entity.Quantity = award.quantity.Value;
            if (award.target.HasValue) entity.Target = award.target.Value;

            await StorageContext.AwardTable.MergeAsync(entity);
            InvalidateAwardsCache(entity.PartitionKey);
            return entity;
        }

        #endregion

        private string GenerateAssignmentId(string awardId, string assigneeId)
        {
            return DigestHelper.String2Guid($"{awardId}-{assigneeId}".ToLower()).ToString();
        }

        #region CreateOrUpdateAssignmentAsync
        public async Task<AwardAssignmentEntity> CreateOrUpdateAssignmentAsync(AwardAssignment request, CancellationToken cancellationToken = default)
        {
            string assignmentId = GenerateAssignmentId(request.awardId, request.assigneeId);
            var assignment = new AwardAssignmentEntity
            {
                PartitionKey = request.hackathonName,
                RowKey = GenerateAssignmentId(request.awardId, request.assigneeId),
                AssigneeId = request.assigneeId,
                AwardId = request.awardId,
                CreatedAt = DateTime.UtcNow,
                Description = request.description,
            };
            await StorageContext.AwardAssignmentTable.InsertOrReplaceAsync(assignment, cancellationToken);

            return assignment;
        }
        #endregion

        #region UpdateAssignmentAsync
        public async Task<AwardAssignmentEntity> UpdateAssignmentAsync(AwardAssignmentEntity existing, AwardAssignment request, CancellationToken cancellationToken = default)
        {
            if (existing == null || request == null)
                return existing;

            existing.Description = request.description ?? existing.Description;
            await StorageContext.AwardAssignmentTable.MergeAsync(existing, cancellationToken);
            return existing;
        }
        #endregion

        #region GetAssignmentCountAsync
        public async Task<int> GetAssignmentCountAsync(string hackathonName, string awardId, CancellationToken cancellationToken = default)
        {
            var allAssignment = await ListByAwardAsync(hackathonName, awardId, cancellationToken);
            return allAssignment.Count();
        }
        #endregion

        #region GetAssignmentAsync
        public async Task<AwardAssignmentEntity> GetAssignmentAsync(string hackathonName, string assignmentId, CancellationToken cancellationToken = default)
        {
            if (string.IsNullOrWhiteSpace(hackathonName) || string.IsNullOrWhiteSpace(assignmentId))
                return null;

            return await StorageContext.AwardAssignmentTable.RetrieveAsync(hackathonName, assignmentId, cancellationToken);
        }
        #endregion

        #region ListPaginatedAssignmentsAsync

        public async Task<IEnumerable<AwardAssignmentEntity>> ListPaginatedAssignmentsAsync(string hackathonName, AwardAssignmentQueryOptions options, CancellationToken cancellationToken = default)
        {
            IEnumerable<AwardAssignmentEntity> awardAssignments = new List<AwardAssignmentEntity>();
            switch (options.QueryType)
            {
                case AwardAssignmentQueryType.Award:
                    awardAssignments = await ListByAwardAsync(hackathonName, options.AwardId, cancellationToken);
                    break;
                case AwardAssignmentQueryType.Team:
                    awardAssignments = await ListAssignmentsByTeamAsync(hackathonName, options.TeamId, cancellationToken);
                    break;
                case AwardAssignmentQueryType.Hackathon:
                    awardAssignments = await ListByHackathonAsync(hackathonName, cancellationToken);
                    break;
                default:
                    break;
            }

            // paging
            int.TryParse(options.TableContinuationToken?.NextPartitionKey, out int np);
            int top = options.Top.GetValueOrDefault(100);
            var assignments = awardAssignments.OrderByDescending(a => a.CreatedAt)
                .Skip(np)
                .Take(top);

            // next paging
            options.Next = null;
            if (np + top < awardAssignments.Count())
            {
                options.Next = new TableContinuationToken
                {
                    NextPartitionKey = (np + top).ToString(),
                    NextRowKey = (np + top).ToString(),
                };
            }

            return assignments;
        }

        #endregion

        #region ListAssignmentsByTeamAsync
        public async Task<IEnumerable<AwardAssignmentEntity>> ListAssignmentsByTeamAsync(string hackathonName, string teamId, CancellationToken cancellationToken = default)
        {
            if (string.IsNullOrWhiteSpace(hackathonName) || string.IsNullOrWhiteSpace(teamId))
                return new List<AwardAssignmentEntity>();

            return await StorageContext.AwardAssignmentTable.ListByAssigneeAsync(hackathonName, teamId, cancellationToken);
        }
        #endregion

        #region DeleteAssignmentAsync
        public async Task DeleteAssignmentAsync(string hackathonName, string assignmentId, CancellationToken cancellationToken = default)
        {
            await StorageContext.AwardAssignmentTable.DeleteAsync(hackathonName, assignmentId, cancellationToken);
        }
        #endregion
    }
}
