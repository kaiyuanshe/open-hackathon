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
    public interface IHackathonManagement
    {
        /// <summary>
        /// Create a new hackathon
        /// </summary>
        /// <param name="request"></param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<HackathonEntity> CreateHackathonAsync(Hackathon request, CancellationToken cancellationToken);
      
        /// <summary>
        /// Get Hackathon By name. Return null if not found.
        /// </summary>
        /// <returns></returns>
        Task<HackathonEntity> GetHackathonEntityByNameAsync(string name, CancellationToken cancellationToken);

        /// <summary>
        /// Search hackathon
        /// </summary>
        /// <param name="options"></param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<IEnumerable<HackathonEntity>> SearchHackathonAsync(HackathonSearchOptions options, CancellationToken cancellationToken = default);
      
        /// <summary>
        /// Update hackathon from request.
        /// </summary>
        /// <param name="request"></param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<HackathonEntity> UpdateHackathonAsync(Hackathon request, CancellationToken cancellationToken);
    }

    public class HackathonManagement : ManagementClientBase, IHackathonManagement
    {
        public async Task<HackathonEntity> CreateHackathonAsync(Hackathon request, CancellationToken cancellationToken)
        {
            #region Insert HackathonEntity
            var entity = new HackathonEntity
            {
                PartitionKey = request.Name,
                RowKey = string.Empty,
                AutoApprove = request.AutoApprove.HasValue ? request.AutoApprove.Value : false,
                Ribbon = request.Ribbon,
                Status = Models.Enums.HackathonStatus.Planning,
                Summary = request.Summary,
                Tags = request.Tags,
                MaxEnrollment = request.MaxEnrollment.HasValue ? request.MaxEnrollment.Value : 0,
                Banners = request.Banners,
                CreateTime = DateTime.UtcNow,
                CreatorId = request.CreatorId,
                Detail = request.Detail,
                DisplayName = request.DisplayName,
                EventStartTime = request.EventStartTime,
                EventEndTime = request.EventEndTime,
                EnrollmentStartTime = request.EnrollmentStartTime,
                EnrollmentEndTime = request.EnrollmentEndTime,
                JudgeStartTime = request.JudgeStartTime,
                JudgeEndTime = request.JudgeEndTime,
                Location = request.Location,
            };
            await StorageContext.HackathonTable.InsertAsync(entity, cancellationToken);
            #endregion

            #region Add creator as Admin
            ParticipantEntity participant = new ParticipantEntity
            {
                PartitionKey = request.Name,
                RowKey = request.CreatorId,
                CreateTime = DateTime.UtcNow,
                Role = ParticipantRole.Administrator,
            };
            await StorageContext.ParticipantTable.InsertAsync(participant, cancellationToken);
            #endregion

            return entity;
        }

        public async Task<HackathonEntity> GetHackathonEntityByNameAsync(string name, CancellationToken cancellationToken = default)
        {
            var entity = await StorageContext.HackathonTable.RetrieveAsync(name, string.Empty, cancellationToken);
            return entity;
        }

        public async Task<IEnumerable<HackathonEntity>> SearchHackathonAsync(HackathonSearchOptions options, CancellationToken cancellationToken = default)
        {
            var entities = new List<HackathonEntity>();
            await StorageContext.HackathonTable.ExecuteQuerySegmentedAsync(null, (segment) =>
            {
                entities.AddRange(segment);
            }, cancellationToken);

            return entities;
        }

        public async Task<HackathonEntity> UpdateHackathonAsync(Hackathon request, CancellationToken cancellationToken)
        {
            await StorageContext.HackathonTable.RetrieveAndMergeAsync(request.Name, string.Empty, (entity) =>
            {
                entity.Ribbon = request.Ribbon ?? entity.Ribbon;
                entity.Summary = request.Summary ?? entity.Summary;
                entity.Detail = request.Detail ?? entity.Detail;
                entity.Location = request.Location ?? entity.Location;
                entity.Banners = request.Banners ?? entity.Banners;
                entity.DisplayName = request.DisplayName ?? entity.DisplayName;
                if (request.MaxEnrollment.HasValue)
                    entity.MaxEnrollment = request.MaxEnrollment.Value;
                if (request.AutoApprove.HasValue)
                    entity.AutoApprove = request.AutoApprove.Value;
                entity.Tags = request.Tags ?? entity.Tags;
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
            return await StorageContext.HackathonTable.RetrieveAsync(request.Name, string.Empty, cancellationToken);
        }
    }

    public class HackathonSearchOptions
    {

    }
}
