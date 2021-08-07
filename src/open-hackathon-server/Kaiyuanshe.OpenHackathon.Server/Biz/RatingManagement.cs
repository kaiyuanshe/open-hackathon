using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.Extensions.Logging;
using System;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Biz
{
    public interface IRatingManagement
    {
        Task<RatingKindEntity> CreateRatingKindAsync(RatingKind parameter, CancellationToken cancellationToken);
    }

    public class RatingManagement : ManagementClientBase, IRatingManagement
    {
        private readonly ILogger Logger;

        public RatingManagement(ILogger<RatingManagement> logger)
        {
            Logger = logger;
        }

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
            return entity;
        }
        #endregion
    }
}
