using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.WindowsAzure.Storage;
using Microsoft.WindowsAzure.Storage.Table;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.Tables
{
    public interface ITeamWorkTable : IAzureTable<TeamWorkEntity>
    {
        Task<IEnumerable<TeamWorkEntity>> ListByTeamAsync(string hackathonName, string teamId, CancellationToken cancellationToken = default);
    }

    public class TeamWorkTable : AzureTable<TeamWorkEntity>, ITeamWorkTable
    {
        public TeamWorkTable()
        {
            // UT only
        }

        public TeamWorkTable(CloudStorageAccount storageAccount, string tableName)
              : base(storageAccount, tableName)
        {
        }

        public async Task<IEnumerable<TeamWorkEntity>> ListByTeamAsync(string hackathonName, string teamId, CancellationToken cancellationToken = default)
        {
            List<TeamWorkEntity> list = new List<TeamWorkEntity>();

            var pkFilter = TableQueryHelper.PartitionKeyFilter(hackathonName);
            var teamIdFilter=TableQuery.GenerateFilterCondition(nameof(TeamWorkEntity.TeamId),
                           QueryComparisons.Equal,
                           teamId);
            var filter = TableQueryHelper.And(pkFilter, teamIdFilter);

            TableQuery<TeamWorkEntity> query = new TableQuery<TeamWorkEntity>().Where(filter);
            await ExecuteQuerySegmentedAsync(query, (segment) =>
            {
                list.AddRange(segment);
            }, cancellationToken);

            return list;
        }
    }
}
