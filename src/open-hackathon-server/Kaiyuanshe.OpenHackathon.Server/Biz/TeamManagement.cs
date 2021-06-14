using Kaiyuanshe.OpenHackathon.Server.Cache;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Storage;
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
        /// Update a team. Team Admin only
        /// </summary>
        /// <param name="request">client request</param>
        /// <param name="teamEntity">entity to update</param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<TeamEntity> UpdateTeamAsync(Team request, TeamEntity teamEntity, CancellationToken cancellationToken = default);

        /// <summary>
        /// Get a team by team Id
        /// </summary>
        /// <param name="hackathonName">name of hackathon</param>
        /// <param name="teamId">unique id of the team</param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<TeamEntity> GetTeamByIdAsync(string hackathonName, string teamId, CancellationToken cancellationToken = default);

        /// <summary>
        /// Delete a team
        /// </summary>
        /// <param name="team"></param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task DeleteTeamAsync(TeamEntity team, CancellationToken cancellationToken = default);

        /// <summary>
        /// List paged teams of hackathon
        /// </summary>
        /// <param name="hackathonName">name of hackathon</param>
        /// <param name="options">options for query</param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<TableQuerySegment<TeamEntity>> ListPaginatedTeamsAsync(string hackathonName, TeamQueryOptions options, CancellationToken cancellationToken = default);

        /// <summary>
        /// List all team members
        /// </summary>
        /// <param name="teamId">guid of the team</param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<IEnumerable<TeamMemberEntity>> ListTeamMembersAsync(string teamId, CancellationToken cancellationToken = default);

        /// <summary>
        /// List paginated team members with optional filters
        /// </summary>
        /// <param name="teamId">guid of the team</param>
        /// <param name="options">options for query</param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<TableQuerySegment<TeamMemberEntity>> ListPaginatedTeamMembersAsync(string teamId, TeamMemberQueryOptions options, CancellationToken cancellationToken = default);


        /// <summary>
        /// Get a team member by userId
        /// </summary>
        /// <param name="teamId"></param>
        /// <param name="userId"></param>
        /// <param name="cancellationToken"></param>
        /// <returns>the team member</returns>
        Task<TeamMemberEntity> GetTeamMemberAsync(string teamId, string userId, CancellationToken cancellationToken = default);

        /// <summary>
        /// Create a new team member. Not existance check. Please check existance before call this method
        /// </summary>
        /// <param name="request"></param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<TeamMemberEntity> CreateTeamMemberAsync(TeamMember request, CancellationToken cancellationToken = default);

        /// <summary>
        /// Upldate a team member(not including status/role). Not existance check. Please check existance before call this method
        /// </summary>
        /// <param name="request"></param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<TeamMemberEntity> UpdateTeamMemberAsync(TeamMemberEntity member, TeamMember request, CancellationToken cancellationToken = default);

        /// <summary>
        /// Update the status of a member
        /// </summary>
        /// <param name="member"></param>
        /// <param name="teamMemberStatus"></param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<TeamMemberEntity> UpdateTeamMemberStatusAsync(TeamMemberEntity member, TeamMemberStatus teamMemberStatus, CancellationToken cancellationToken = default);

        /// <summary>
        /// Update the status of a member
        /// </summary>
        /// <param name="member"></param>
        /// <param name="teamMemberRole"></param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<TeamMemberEntity> UpdateTeamMemberRoleAsync(TeamMemberEntity member, TeamMemberRole teamMemberRole, CancellationToken cancellationToken = default);

        /// <summary>
        /// Delete a team memter
        /// </summary>
        /// <param name="member"></param>
        /// <param name="cancellationToken"></param>
        Task DeleteTeamMemberAsync(TeamMemberEntity member, CancellationToken cancellationToken = default);
    }

    /// <inheritdoc cref="ITeamManagement"/>
    public class TeamManagement : ManagementClientBase, ITeamManagement
    {
        private readonly ILogger Logger;

        public TeamManagement(ILogger<TeamManagement> logger)
        {
            Logger = logger;
        }

        public async Task<TeamMemberEntity> CreateTeamMemberAsync(TeamMember request, CancellationToken cancellationToken = default)
        {
            var entity = new TeamMemberEntity
            {
                CreatedAt = DateTime.UtcNow,
                Description = request.description,
                HackathonName = request.hackathonName,
                PartitionKey = request.teamId,
                RowKey = request.userId,
                Role = request.role.GetValueOrDefault(TeamMemberRole.Member),
                Status = request.status,
            };

            await StorageContext.TeamMemberTable.InsertAsync(entity);

            return entity;
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
                AutoApprove = request.autoApprove.GetValueOrDefault(false),
                Description = request.description,
                DisplayName = request.displayName,
                CreatorId = request.creatorId,
                CreatedAt = DateTime.UtcNow,
            };
            if (string.IsNullOrWhiteSpace(request.displayName))
            {
                teamEntity.DisplayName = teamEntity.RowKey;
            }
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

        public async Task<TeamEntity> GetTeamByIdAsync(string hackathonName, string teamId, CancellationToken cancellationToken = default)
        {
            if (string.IsNullOrWhiteSpace(hackathonName) || string.IsNullOrWhiteSpace(teamId))
                return null;

            return await StorageContext.TeamTable.RetrieveAsync(hackathonName.ToLower(), teamId, cancellationToken);
        }

        public async Task<TeamMemberEntity> GetTeamMemberAsync(string teamId, string userId, CancellationToken cancellationToken = default)
        {
            if (string.IsNullOrWhiteSpace(teamId) || string.IsNullOrWhiteSpace(userId))
                return null;

            return await StorageContext.TeamMemberTable.RetrieveAsync(teamId, userId, cancellationToken);
        }

        public async Task<IEnumerable<TeamMemberEntity>> ListTeamMembersAsync(string teamId, CancellationToken cancellationToken = default)
        {
            Func<CancellationToken, Task<IEnumerable<TeamMemberEntity>>> supplyValue = async (ct) =>
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
                    var segment = await StorageContext.TeamMemberTable.ExecuteQuerySegmentedAsync(query, continuationToken, ct);
                    members.AddRange(segment);
                } while (continuationToken != null);
                return members;
            };

            string cacheKey = $"team_members_{teamId}";
            return await Cache.GetOrAddAsync(cacheKey, CachePolicies.ExpireIn1M, supplyValue, false, cancellationToken);
        }

        public async Task<TeamEntity> UpdateTeamAsync(Team request, TeamEntity teamEntity, CancellationToken cancellationToken = default)
        {
            if (teamEntity == null || request == null)
                return teamEntity;

            teamEntity.AutoApprove = request.autoApprove.GetValueOrDefault(teamEntity.AutoApprove);
            teamEntity.Description = request.description ?? teamEntity.Description;
            teamEntity.DisplayName = request.displayName ?? teamEntity.DisplayName;

            await StorageContext.TeamTable.MergeAsync(teamEntity, cancellationToken);
            return teamEntity;
        }

        public async Task<TeamMemberEntity> UpdateTeamMemberAsync(TeamMemberEntity member, TeamMember request, CancellationToken cancellationToken = default)
        {
            if (member == null || request == null)
                return member;

            member.Description = request.description ?? member.Description;
            await StorageContext.TeamMemberTable.MergeAsync(member, cancellationToken);
            return member;
        }

        public async Task<TeamMemberEntity> UpdateTeamMemberStatusAsync(TeamMemberEntity member, TeamMemberStatus teamMemberStatus, CancellationToken cancellationToken = default)
        {
            if (member == null)
                return member;

            if (member.Status != teamMemberStatus)
            {
                member.Status = teamMemberStatus;
                await StorageContext.TeamMemberTable.MergeAsync(member);
            }

            return member;
        }

        public async Task DeleteTeamMemberAsync(TeamMemberEntity member, CancellationToken cancellationToken = default)
        {
            if (member == null)
                return;

            await StorageContext.TeamMemberTable.DeleteAsync(member.TeamId, member.UserId);
        }

        public async Task DeleteTeamAsync(TeamEntity team, CancellationToken cancellationToken = default)
        {
            if (team == null)
                return;

            await StorageContext.TeamTable.DeleteAsync(team.PartitionKey, team.RowKey, cancellationToken);
        }

        public async Task<TeamMemberEntity> UpdateTeamMemberRoleAsync(TeamMemberEntity member, TeamMemberRole teamMemberRole, CancellationToken cancellationToken = default)
        {
            if (member == null)
                return member;

            if (member.Role != teamMemberRole)
            {
                member.Role = teamMemberRole;
                await StorageContext.TeamMemberTable.MergeAsync(member);
            }

            return member;
        }

        public async Task<TableQuerySegment<TeamEntity>> ListPaginatedTeamsAsync(string hackathonName, TeamQueryOptions options, CancellationToken cancellationToken = default)
        {
            var filter = TableQuery.GenerateFilterCondition(
                           nameof(TeamEntity.PartitionKey),
                           QueryComparisons.Equal,
                           hackathonName);

            int top = 100;
            if (options != null && options.Top.HasValue && options.Top.Value > 0)
            {
                top = options.Top.Value;
            }
            TableQuery<TeamEntity> query = new TableQuery<TeamEntity>()
                .Where(filter)
                .Take(top);

            TableContinuationToken continuationToken = options?.TableContinuationToken;
            return await StorageContext.TeamTable.ExecuteQuerySegmentedAsync(query, continuationToken, cancellationToken);
        }

        public async Task<TableQuerySegment<TeamMemberEntity>> ListPaginatedTeamMembersAsync(string teamId, TeamMemberQueryOptions options, CancellationToken cancellationToken = default)
        {
            var filter = TableQuery.GenerateFilterCondition(
                           nameof(TeamMemberEntity.PartitionKey),
                           QueryComparisons.Equal,
                           teamId);

            if (options != null)
            {
                if (options.Status.HasValue)
                {
                    var statusFilter = TableQuery.GenerateFilterConditionForInt(
                        nameof(TeamMemberEntity.Status),
                        QueryComparisons.Equal,
                        (int)options.Status.Value);
                    filter = TableQueryHelper.And(filter, statusFilter);
                }
                if (options.Role.HasValue)
                {
                    var roleFilter = TableQuery.GenerateFilterConditionForInt(
                        nameof(TeamMemberEntity.Role),
                        QueryComparisons.Equal,
                        (int)options.Role.Value);
                    filter = TableQueryHelper.And(filter, roleFilter);
                }
            }

            int top = 100;
            if (options != null && options.Top.HasValue && options.Top.Value > 0)
            {
                top = options.Top.Value;
            }
            TableQuery<TeamMemberEntity> query = new TableQuery<TeamMemberEntity>()
                .Where(filter)
                .Take(top);

            TableContinuationToken continuationToken = options?.TableContinuationToken;
            return await StorageContext.TeamMemberTable.ExecuteQuerySegmentedAsync(query, continuationToken, cancellationToken);

        }
    }
}
