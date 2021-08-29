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
        /// Get team(s) by team name
        /// </summary>
        Task<IEnumerable<TeamEntity>> GetTeamByNameAsync(string hackathonName, string teamName, CancellationToken cancellationToken = default);

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
        Task<IEnumerable<TeamMemberEntity>> ListTeamMembersAsync(string hackathonName, string teamId, CancellationToken cancellationToken = default);

        /// <summary>
        /// List paginated team members with optional filters
        /// </summary>
        Task<TableQuerySegment<TeamMemberEntity>> ListPaginatedTeamMembersAsync(string hackathonName, string teamId, TeamMemberQueryOptions options, CancellationToken cancellationToken = default);

        /// <summary>
        /// Get a team member by userId
        /// </summary>
        Task<TeamMemberEntity> GetTeamMemberAsync(string hackathonName, string userId, CancellationToken cancellationToken = default);

        /// <summary>
        /// Create a new team member. Not existance check. Please check existance before call this method
        /// </summary>
        Task<TeamMemberEntity> CreateTeamMemberAsync(TeamMember request, CancellationToken cancellationToken = default);

        /// <summary>
        /// Upldate a team member(not including status/role). Not existance check. Please check existance before call this method
        /// </summary>
        Task<TeamMemberEntity> UpdateTeamMemberAsync(TeamMemberEntity member, TeamMember request, CancellationToken cancellationToken = default);

        /// <summary>
        /// Update the status of a member
        /// </summary>
        Task<TeamMemberEntity> UpdateTeamMemberStatusAsync(TeamMemberEntity member, TeamMemberStatus teamMemberStatus, CancellationToken cancellationToken = default);

        /// <summary>
        /// Update the status of a member
        /// </summary>
        Task<TeamMemberEntity> UpdateTeamMemberRoleAsync(TeamMemberEntity member, TeamMemberRole teamMemberRole, CancellationToken cancellationToken = default);

        /// <summary>
        /// Delete a team memter
        /// </summary>
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

        #region Cache
        private string TeamCacheKey(string teamId)
        {
            return CacheKeys.GetCacheKey(CacheEntryType.Team, teamId);
        }

        private void InvalidateCachedTeam(string teamId)
        {
            string cacheKey = TeamCacheKey(teamId);
            Cache.Remove(cacheKey);
        }
        #endregion

        #region CreateTeamAsync
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
                MembersCount = 1,
            };
            if (string.IsNullOrWhiteSpace(request.displayName))
            {
                teamEntity.DisplayName = teamEntity.RowKey;
            }
            await StorageContext.TeamTable.InsertAsync(teamEntity, cancellationToken);

            TeamMemberEntity teamMember = new TeamMemberEntity
            {
                TeamId = teamEntity.Id,
                RowKey = request.creatorId,
                PartitionKey = request.hackathonName,
                Description = "Creator",
                Role = TeamMemberRole.Admin,
                Status = TeamMemberStatus.approved,
                CreatedAt = teamEntity.CreatedAt,
            };
            await StorageContext.TeamMemberTable.InsertAsync(teamMember, cancellationToken);

            return teamEntity;
        }
        #endregion

        #region UpdateTeamAsync
        public async Task<TeamEntity> UpdateTeamAsync(Team request, TeamEntity teamEntity, CancellationToken cancellationToken = default)
        {
            if (teamEntity == null || request == null)
                return teamEntity;

            teamEntity.AutoApprove = request.autoApprove.GetValueOrDefault(teamEntity.AutoApprove);
            teamEntity.Description = request.description ?? teamEntity.Description;
            teamEntity.DisplayName = request.displayName ?? teamEntity.DisplayName;

            await StorageContext.TeamTable.MergeAsync(teamEntity, cancellationToken);
            InvalidateCachedTeam(teamEntity.Id);
            return teamEntity;
        }
        #endregion

        #region UpdateTeamMembersCountAsync
        public async Task UpdateTeamMembersCountAsync(string hackathonName, string teamId, CancellationToken cancellationToken = default)
        {
            var team = await StorageContext.TeamTable.RetrieveAsync(hackathonName, teamId, cancellationToken);
            if (team != null)
            {
                var count = await StorageContext.TeamMemberTable.GetMemberCountAsync(hackathonName, teamId, cancellationToken);
                team.MembersCount = count;
                await StorageContext.TeamTable.MergeAsync(team, cancellationToken);
                InvalidateCachedTeam(teamId);
            }
        }
        #endregion

        #region GetTeamByIdAsync
        public async Task<TeamEntity> GetTeamByIdAsync(string hackathonName, string teamId, CancellationToken cancellationToken = default)
        {
            if (string.IsNullOrWhiteSpace(hackathonName) || string.IsNullOrWhiteSpace(teamId))
                return null;

            return await Cache.GetOrAddAsync(
                TeamCacheKey(teamId),
                TimeSpan.FromHours(12),
                (ct) => StorageContext.TeamTable.RetrieveAsync(hackathonName.ToLower(), teamId, ct),
                false,
                cancellationToken);
        }
        #endregion

        #region GetTeamByNameAsync
        public async Task<IEnumerable<TeamEntity>> GetTeamByNameAsync(string hackathonName, string teamName, CancellationToken cancellationToken = default)
        {
            var filter = TableQueryHelper.And(
                TableQuery.GenerateFilterCondition(nameof(TeamEntity.PartitionKey), QueryComparisons.Equal, hackathonName),
                TableQuery.GenerateFilterCondition(nameof(TeamEntity.DisplayName), QueryComparisons.Equal, teamName)
                );

            TableQuery<TeamEntity> query = new TableQuery<TeamEntity>().Where(filter);

            List<TeamEntity> list = new List<TeamEntity>();
            await StorageContext.TeamTable.ExecuteQuerySegmentedAsync(query, (segment) =>
            {
                list.AddRange(segment);
            }, cancellationToken);

            return list;
        }
        #endregion

        #region ListPaginatedTeamsAsync
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
        #endregion

        #region DeleteTeamAsync
        public async Task DeleteTeamAsync(TeamEntity team, CancellationToken cancellationToken = default)
        {
            if (team == null)
                return;

            await StorageContext.TeamTable.DeleteAsync(team.PartitionKey, team.RowKey, cancellationToken);
            InvalidateCachedTeam(team.Id);
        }
        #endregion

        #region CreateTeamMemberAsync
        public async Task<TeamMemberEntity> CreateTeamMemberAsync(TeamMember request, CancellationToken cancellationToken = default)
        {
            var entity = new TeamMemberEntity
            {
                CreatedAt = DateTime.UtcNow,
                Description = request.description,
                PartitionKey = request.hackathonName,
                TeamId = request.teamId,
                RowKey = request.userId,
                Role = request.role.GetValueOrDefault(TeamMemberRole.Member),
                Status = request.status,
            };

            await StorageContext.TeamMemberTable.InsertOrMergeAsync(entity);
            await UpdateTeamMembersCountAsync(request.hackathonName, request.teamId, cancellationToken);
            return entity;
        }
        #endregion

        #region UpdateTeamMemberAsync
        public async Task<TeamMemberEntity> UpdateTeamMemberAsync(TeamMemberEntity member, TeamMember request, CancellationToken cancellationToken = default)
        {
            if (member == null || request == null)
                return member;

            member.Description = request.description ?? member.Description;
            await StorageContext.TeamMemberTable.MergeAsync(member, cancellationToken);
            return member;
        }
        #endregion

        #region GetTeamMemberAsync
        public async Task<TeamMemberEntity> GetTeamMemberAsync(string hackathonName, string userId, CancellationToken cancellationToken = default)
        {
            if (string.IsNullOrWhiteSpace(hackathonName) || string.IsNullOrWhiteSpace(userId))
                return null;

            return await StorageContext.TeamMemberTable.RetrieveAsync(hackathonName, userId, cancellationToken);
        }
        #endregion

        #region UpdateTeamMemberStatusAsync
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
        #endregion

        #region UpdateTeamMemberRoleAsync
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
        #endregion

        #region DeleteTeamMemberAsync
        public async Task DeleteTeamMemberAsync(TeamMemberEntity member, CancellationToken cancellationToken = default)
        {
            if (member == null)
                return;

            await StorageContext.TeamMemberTable.DeleteAsync(member.PartitionKey, member.RowKey, cancellationToken);
            await UpdateTeamMembersCountAsync(member.HackathonName, member.TeamId, cancellationToken);
        }
        #endregion

        #region ListTeamMembersAsync
        public async Task<IEnumerable<TeamMemberEntity>> ListTeamMembersAsync(string hackathonName, string teamId, CancellationToken cancellationToken = default)
        {
            Func<CancellationToken, Task<IEnumerable<TeamMemberEntity>>> supplyValue = async (ct) =>
            {
                var pkFilter = TableQueryHelper.PartitionKeyFilter(hackathonName);
                var teamIdFilter = TableQuery.GenerateFilterCondition(nameof(TeamMemberEntity.TeamId), QueryComparisons.Equal, teamId);
                var filter = TableQueryHelper.And(pkFilter, teamIdFilter);

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
            return await Cache.GetOrAddAsync(cacheKey, TimeSpan.FromMinutes(1), supplyValue, false, cancellationToken);
        }
        #endregion

        #region ListPaginatedTeamMembersAsync
        public async Task<TableQuerySegment<TeamMemberEntity>> ListPaginatedTeamMembersAsync(string hackathonName, string teamId, TeamMemberQueryOptions options, CancellationToken cancellationToken = default)
        {
            var pkFilter = TableQueryHelper.PartitionKeyFilter(hackathonName);
            var teamIdFilter = TableQuery.GenerateFilterCondition(nameof(TeamMemberEntity.TeamId), QueryComparisons.Equal, teamId);
            var filter = TableQueryHelper.And(pkFilter, teamIdFilter);

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
        #endregion
    }
}
