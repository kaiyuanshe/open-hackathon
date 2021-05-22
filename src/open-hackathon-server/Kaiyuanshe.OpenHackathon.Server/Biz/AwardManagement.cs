using Kaiyuanshe.OpenHackathon.Server.Models;
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

        /// <summary>
        /// Create a new Award. No existeance check.
        /// </summary>
        /// <param name="hackathonName">name of hackathon</param>
        /// <param name="award">award from request</param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<AwardEntity> CreateAwardAsync(string hackathonName, Award award, CancellationToken cancellationToken = default);

        /// <summary>
        /// Update a new Award. No existeance check.
        /// </summary>
        /// <param name="entity">award to update.</param>
        /// <param name="award">award from request</param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<AwardEntity> UpdateAwardAsync(AwardEntity entity, Award award, CancellationToken cancellationToken = default);

    }


    public class AwardManagement : ManagementClientBase, IAwardManagement
    {
        private readonly ILogger Logger;

        public AwardManagement(ILogger<AwardManagement> logger)
        {
            Logger = logger;
        }

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
            return awardEnity;
        }

        public async Task<AwardEntity> GeAwardByIdAsync(string hackathonName, string awardId, CancellationToken cancellationToken = default)
        {
            if (string.IsNullOrWhiteSpace(hackathonName) || string.IsNullOrWhiteSpace(awardId))
                return null;

            return await StorageContext.AwardTable.RetrieveAsync(hackathonName.ToLower(), awardId, cancellationToken);
        }

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
            return entity;
        }
    }
}
