using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.Extensions.Logging;
using Microsoft.WindowsAzure.Storage.Table;
using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Biz
{
    public interface ITeamManagement
    {
        /// <summary>
        /// Create a new team. The creator will be added as team admin
        /// </summary>
        /// <param name="request"></param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<TeamEntity> CreateTeamAsync(Team request, CancellationToken cancellationToken = default);

        /// <summary>
        /// List all team members
        /// </summary>
        /// <param name="teamId">guid of the team</param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<IEnumerable<TeamMemberEntity>> ListTeamMembersAsync(string teamId, CancellationToken cancellationToken = default);
    }

    public class TeamManagement : ManagementClientBase, ITeamManagement
    {
        private readonly ILogger Logger;

        public TeamManagement(ILogger<TeamManagement> logger)
        {
            Logger = logger;
        }

        public async Task<TeamEntity> CreateTeamAsync(Team request, CancellationToken cancellationToken = default)
        {
            if (string.IsNullOrWhiteSpace(request.hackathonName)
                || string.IsNullOrWhiteSpace(request.creatorId))
            {
                Logger.LogInformation($"cannot create team. hackathonName or creatorId is empty");
                return null;
            }

            TeamEntity teamEntity = new TeamEntity
            {
                PartitionKey = request.hackathonName,
                RowKey = Guid.NewGuid().ToString(),
                AutoApprove = request.autoApprove,
                Description = request.description,
                DisplayName = request.displayName,
                CreatorId = request.creatorId,
                CreatedAt = DateTime.UtcNow,
            };
            await StorageContext.TeamTable.InsertAsync(teamEntity, cancellationToken);

            TeamMemberEntity teamMember = new TeamMemberEntity
            {
                PartitionKey = teamEntity.Id,
                RowKey = request.creatorId,
                HackathonName = request.hackathonName,
                Description = "Creator",
                Role = TeamMemberRole.Admin,
                Status = TeamMemberStatus.approved,
                CreatedAt = teamEntity.CreatedAt,
            };
            await StorageContext.TeamMemberTable.InsertAsync(teamMember, cancellationToken);

            return teamEntity;
        }

        public async Task<IEnumerable<TeamMemberEntity>> ListTeamMembersAsync(string teamId, CancellationToken cancellationToken = default)
        {
            Func<Task<IEnumerable<TeamMemberEntity>>> supplyValue = async () =>
            {
                var filter = TableQuery.GenerateFilterCondition(
                              nameof(EnrollmentEntity.PartitionKey),
                              QueryComparisons.Equal,
                              teamId);

                TableQuery<TeamMemberEntity> query = new TableQuery<TeamMemberEntity>().Where(filter);

                List<TeamMemberEntity> members = new List<TeamMemberEntity>();
                TableContinuationToken continuationToken = null;
                do
                {
                    var segment = await StorageContext.TeamMemberTable.ExecuteQuerySegmentedAsync(query, continuationToken, cancellationToken);
                    members.AddRange(segment);
                } while (continuationToken != null);
                return members;
            };

            string cacheKey = $"team_members_{teamId}";
            return await CacheHelper.GetOrAddAsync(cacheKey, supplyValue, CacheHelper.ExpireIn1M);
        }
    }
}
