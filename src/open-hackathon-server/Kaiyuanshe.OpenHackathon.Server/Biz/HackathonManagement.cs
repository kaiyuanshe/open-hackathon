using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Storage;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.Extensions.Logging;
using Microsoft.WindowsAzure.Storage.Table;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.Caching;
using System.Threading;
using System.Threading.Tasks;


namespace Kaiyuanshe.OpenHackathon.Server.Biz
{
    public interface IHackathonManagement
    {
        #region Hackathon
        /// <summary>
        /// Create a new hackathon
        /// </summary>
        /// <param name="request"></param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<HackathonEntity> CreateHackathonAsync(Hackathon request, CancellationToken cancellationToken = default);

        /// <summary>
        /// Update hackathon from request.
        /// </summary>
        /// <param name="request"></param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<HackathonEntity> UpdateHackathonAsync(Hackathon request, CancellationToken cancellationToken = default);

        /// <summary>
        /// Change the hackathon to Deleted.
        /// </summary>
        /// <param name="name"></param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task DeleteHackathonLogically(string name, CancellationToken cancellationToken = default);

        /// <summary>
        /// Get Hackathon By name. Return null if not found.
        /// </summary>
        /// <returns></returns>
        Task<HackathonEntity> GetHackathonEntityByNameAsync(string name, CancellationToken cancellationToken = default);

        /// <summary>
        /// Search hackathon
        /// </summary>
        /// <param name="options"></param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<IEnumerable<HackathonEntity>> SearchHackathonAsync(HackathonSearchOptions options, CancellationToken cancellationToken = default);

        #endregion

        #region Admin
        /// <summary>
        /// List all Administrators of a Hackathon. PlatformAdministrator is not included.
        /// </summary>
        /// <param name="name">name of Hackathon</param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<IEnumerable<ParticipantEntity>> ListHackathonAdminAsync(string name, CancellationToken cancellationToken = default);
        #endregion

        #region Contestant
        /// <summary>
        /// Register a hackathon event as contestant
        /// </summary>
        Task<ParticipantEntity> EnrollAsync(HackathonEntity hackathon, string userId, CancellationToken cancellationToken);
        #endregion
    }

    /// <inheritdoc cref="IHackathonManagement"/>
    public class HackathonManagement : ManagementClientBase, IHackathonManagement
    {
        private readonly ILogger Logger;

        public HackathonManagement(ILogger<HackathonManagement> logger)
        {
            Logger = logger;
        }

        public async Task<HackathonEntity> CreateHackathonAsync(Hackathon request, CancellationToken cancellationToken = default)
        {
            #region Insert HackathonEntity
            var entity = new HackathonEntity
            {
                PartitionKey = request.name,
                RowKey = string.Empty,
                AutoApprove = request.autoApprove.HasValue ? request.autoApprove.Value : false,
                Ribbon = request.ribbon,
                Status = Models.Enums.HackathonStatus.Planning,
                Summary = request.summary,
                Tags = request.tags,
                MaxEnrollment = request.maxEnrollment.HasValue ? request.maxEnrollment.Value : 0,
                Banners = request.banners,
                CreateTime = DateTime.UtcNow,
                CreatorId = request.creatorId,
                Detail = request.detail,
                DisplayName = request.displayName,
                EventStartTime = request.EventStartTime,
                EventEndTime = request.EventEndTime,
                EnrollmentStartTime = request.EnrollmentStartTime,
                EnrollmentEndTime = request.EnrollmentEndTime,
                IsDeleted = false,
                JudgeStartTime = request.JudgeStartTime,
                JudgeEndTime = request.JudgeEndTime,
                Location = request.location,
            };
            await StorageContext.HackathonTable.InsertAsync(entity, cancellationToken);
            #endregion

            #region Add creator as Admin
            ParticipantEntity participant = new ParticipantEntity
            {
                PartitionKey = request.name,
                RowKey = request.creatorId,
                CreateTime = DateTime.UtcNow,
                Role = ParticipantRole.Administrator,
            };
            await StorageContext.ParticipantTable.InsertAsync(participant, cancellationToken);
            #endregion

            return entity;
        }

        public async Task DeleteHackathonLogically(string name, CancellationToken cancellationToken = default)
        {
            await StorageContext.HackathonTable.RetrieveAndMergeAsync(name, string.Empty,
                entity =>
                {
                    entity.IsDeleted = true;
                }, cancellationToken);
        }

        public async Task<HackathonEntity> GetHackathonEntityByNameAsync(string name, CancellationToken cancellationToken = default)
        {
            var entity = await StorageContext.HackathonTable.RetrieveAsync(name, string.Empty, cancellationToken);
            return entity;
        }

        public async Task<IEnumerable<ParticipantEntity>> ListHackathonAdminAsync(string name, CancellationToken cancellationToken = default)
        {
            string cacheKey = CacheKey.Get(CacheKey.Section.HackathonAdmin, name);
            return await CacheHelper.GetOrAddAsync(cacheKey,
                async () =>
                {
                    var allParticipants = await StorageContext.ParticipantTable.ListParticipantsByHackathonAsync(name, cancellationToken);
                    return allParticipants.Where(p => p.Role.HasFlag(ParticipantRole.Administrator));
                },
                CacheHelper.ExpireIn10M);
        }

        public async Task<ParticipantEntity> EnrollAsync(HackathonEntity hackathon, string userId, CancellationToken cancellationToken)
        {
            string hackathonName = hackathon.Name;
            var entity = await StorageContext.ParticipantTable.RetrieveAsync(hackathonName, userId, cancellationToken);

            if (entity != null && entity.Role.HasFlag(ParticipantRole.Contestant))
            {
                Logger.TraceInformation($"Enroll skipped, user with id {userId} alreday enrolled in hackathon {hackathonName}");
                return entity;
            }

            if (entity != null)
            {
                entity.Role = entity.Role | ParticipantRole.Contestant;
                entity.EnrollmentStatus = EnrollmentStatus.Pending;
                if (hackathon.AutoApprove)
                {
                    entity.EnrollmentStatus = EnrollmentStatus.Approved;
                }
                await StorageContext.ParticipantTable.MergeAsync(entity, cancellationToken);
            }
            else
            {
                entity = new ParticipantEntity
                {
                    PartitionKey = hackathonName,
                    RowKey = userId,
                    Role = ParticipantRole.Contestant,
                    EnrollmentStatus = EnrollmentStatus.Pending,
                };
                if (hackathon.AutoApprove)
                {
                    entity.EnrollmentStatus = EnrollmentStatus.Approved;
                }
                await StorageContext.ParticipantTable.InsertAsync(entity, cancellationToken);
            }
            Logger.TraceInformation($"user {userId} enrolled in hackathon {hackathon}, status: {entity.EnrollmentStatus.ToString()}");

            return entity;
        }

        public async Task<IEnumerable<HackathonEntity>> SearchHackathonAsync(HackathonSearchOptions options, CancellationToken cancellationToken = default)
        {
            var entities = new List<HackathonEntity>();
            var filter = TableQuery.GenerateFilterConditionForBool(nameof(HackathonEntity.IsDeleted), QueryComparisons.NotEqual, true);
            TableQuery<HackathonEntity> query = new TableQuery<HackathonEntity>().Where(filter);

            await StorageContext.HackathonTable.ExecuteQuerySegmentedAsync(query, (segment) =>
            {
                entities.AddRange(segment);
            }, cancellationToken);

            return entities;
        }

        public async Task<HackathonEntity> UpdateHackathonAsync(Hackathon request, CancellationToken cancellationToken = default)
        {
            await StorageContext.HackathonTable.RetrieveAndMergeAsync(request.name, string.Empty, (entity) =>
            {
                entity.Ribbon = request.ribbon ?? entity.Ribbon;
                entity.Summary = request.summary ?? entity.Summary;
                entity.Detail = request.detail ?? entity.Detail;
                entity.Location = request.location ?? entity.Location;
                entity.Banners = request.banners ?? entity.Banners;
                entity.DisplayName = request.displayName ?? entity.DisplayName;
                if (request.maxEnrollment.HasValue)
                    entity.MaxEnrollment = request.maxEnrollment.Value;
                if (request.autoApprove.HasValue)
                    entity.AutoApprove = request.autoApprove.Value;
                entity.Tags = request.tags ?? entity.Tags;
                if (request.EventStartTime.HasValue)
                    entity.EventStartTime = request.EventStartTime.Value;
                if (request.EventStartTime.HasValue)
                    entity.EventEndTime = request.EventEndTime.Value;
                if (request.EventStartTime.HasValue)
                    entity.EnrollmentStartTime = request.EnrollmentStartTime.Value;
                if (request.EventStartTime.HasValue)
                    entity.EnrollmentEndTime = request.EnrollmentEndTime.Value;
                if (request.EventStartTime.HasValue)
                    entity.JudgeStartTime = request.JudgeStartTime.Value;
                if (request.EventStartTime.HasValue)
                    entity.JudgeEndTime = request.JudgeEndTime.Value;
            }, cancellationToken);
            return await StorageContext.HackathonTable.RetrieveAsync(request.name, string.Empty, cancellationToken);
        }
    }

    public class HackathonSearchOptions
    {

    }
}
