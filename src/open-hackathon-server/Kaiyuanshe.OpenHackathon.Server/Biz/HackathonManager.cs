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
    public interface IHackathonManager
    {
        /// <summary>
        /// Search hackathon
        /// </summary>
        /// <param name="options"></param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<IEnumerable<HackathonEntity>> SearchHackathonAsync(HackathonSearchOptions options, CancellationToken cancellationToken = default);
        /// <summary>
        /// Get Hackathon By Id. Return null if not found.
        /// </summary>
        /// <param name="id"></param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<HackathonEntity> GetHackathonEntityByIdAsync(string id, CancellationToken cancellationToken);
        /// <summary>
        /// Update hackathon from request.
        /// </summary>
        /// <param name="request"></param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<HackathonEntity> UpdateHackathonAsync(Hackathon request, CancellationToken cancellationToken);
    }

    public class HackathonManager : IHackathonManager
    {
        public IStorageContext StorageContext { get; set; }

        public async Task<IEnumerable<HackathonEntity>> SearchHackathonAsync(HackathonSearchOptions options, CancellationToken cancellationToken = default)
        {
            var entities = new List<HackathonEntity>();
            await StorageContext.HackathonTable.ExecuteQuerySegmentedAsync(null, (segment) =>
            {
                entities.AddRange(segment);
            }, cancellationToken);

            return entities;
        }

        public async Task<HackathonEntity> GetHackathonEntityByIdAsync(string id, CancellationToken cancellationToken = default)
        {
            var entity = await StorageContext.HackathonTable.RetrieveAsync(id, string.Empty, cancellationToken);
            return entity;
        }

        public async Task<HackathonEntity> UpdateHackathonAsync(Hackathon request, CancellationToken cancellationToken)
        {
            await StorageContext.HackathonTable.RetrieveAndMergeAsync(request.Id, string.Empty, (entity) => {
                entity.Name = request.Name;
                entity.Ribbon = request.Ribbon;
                entity.Summary = request.Summary;
                entity.Description = request.Description;
                entity.Location = request.Location;
                entity.Banners = request.Banners;
                entity.MaxEnrollment = request.MaxEnrollment;
                entity.AutoApprove = request.AutoApprove;
                entity.Tags = request.Tags;
                entity.EventStartTime = request.EventStartTime;
                entity.EventEndTime = request.EventEndTime;
                entity.EnrollmentStartTime = request.EnrollmentStartTime;
                entity.EnrollmentEndTime = request.EnrollmentEndTime;
                entity.JudgeStartTime = request.JudgeStartTime;
                entity.JudgeEndTime = request.JudgeEndTime;
            }, cancellationToken);
            return await StorageContext.HackathonTable.RetrieveAsync(request.Id, string.Empty, cancellationToken);
        }
    }

    public class HackathonSearchOptions
    {

    }
}
