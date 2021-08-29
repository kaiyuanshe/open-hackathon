using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.WindowsAzure.Storage;
using Microsoft.WindowsAzure.Storage.Table;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.Tables
{
    public interface ITeamMemberTable : IAzureTable<TeamMemberEntity>
    {
        /// <summary>
        /// Get count of all team members including pendingApproval ones.
        /// </summary>
        Task<int> GetMemberCountAsync(string hackathonName, string teamId, CancellationToken cancellationToken = default);
    }

    public class TeamMemberTable : AzureTable<TeamMemberEntity>, ITeamMemberTable
    {
        internal TeamMemberTable()
        {
            // UT only
        }

        public TeamMemberTable(CloudStorageAccount storageAccount, string tableName)
              : base(storageAccount, tableName)
        {
        }

        #region GetMemberCountAsync
        public async Task<int> GetMemberCountAsync(string hackathonName, string teamId, CancellationToken cancellationToken = default)
        {
            var pkFilter = TableQueryHelper.PartitionKeyFilter(hackathonName);
            var teamIdFilter = TableQuery.GenerateFilterCondition(nameof(TeamMemberEntity.TeamId), QueryComparisons.Equal, teamId);
            var filter = TableQueryHelper.And(pkFilter, teamIdFilter);

            TableQuery<TeamMemberEntity> query = new TableQuery<TeamMemberEntity>()
                .Where(filter)
                .Select(new List<string> { nameof(TeamMemberEntity.RowKey) });

            int count = 0;
            await ExecuteQuerySegmentedAsync(query, (segment) =>
            {
                count += segment.Count();
            }, cancellationToken);

            return count;
        }
        #endregion
    }
}
