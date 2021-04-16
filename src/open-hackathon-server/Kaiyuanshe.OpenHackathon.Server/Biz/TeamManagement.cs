using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.Extensions.Logging;
using System;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Biz
{
    public interface ITeamManagement
    {
        Task<TeamEntity> CreateTeamAsync(Team request, CancellationToken cancellationToken);
    }

    public class TeamManagement : ManagementClientBase, ITeamManagement
    {
        private readonly ILogger Logger;

        public TeamManagement(ILogger<TeamManagement> logger)
        {
            Logger = logger;
        }

        public async Task<TeamEntity> CreateTeamAsync(Team request, CancellationToken cancellationToken)
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
    }
}
