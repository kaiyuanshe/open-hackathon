using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.Extensions.Logging;
using System;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Biz
{
    public interface IWorkManagement
    {
        /// <summary>
        /// Create a new team work. No existance check
        /// </summary>
        /// <returns></returns>
        Task<TeamWorkEntity> CreateTeamWorkAsync(TeamWork request, CancellationToken cancellationToken = default);
    }

    public class WorkManagement : ManagementClientBase, IWorkManagement
    {
        private readonly ILogger Logger;

        public WorkManagement(ILogger<WorkManagement> logger)
        {
            Logger = logger;
        }

        #region CreateTeamWorkAsync
        public async Task<TeamWorkEntity> CreateTeamWorkAsync(TeamWork request, CancellationToken cancellationToken = default)
        {
            if (request == null)
                return null;

            var entity = new TeamWorkEntity
            {
                PartitionKey = request.teamId,
                RowKey = Guid.NewGuid().ToString(),

                CreatedAt = DateTime.UtcNow,
                Description = request.description,
                HackathonName = request.hackathonName,
                Title = request.title,
                Type = request.type.GetValueOrDefault(TeamWorkType.website),
                Url = request.url,
            };
            await StorageContext.TeamWorkTable.InsertAsync(entity);
            return entity;
        }
        #endregion
    }
}
