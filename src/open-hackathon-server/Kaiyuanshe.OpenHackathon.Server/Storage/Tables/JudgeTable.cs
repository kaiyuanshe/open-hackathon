using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.WindowsAzure.Storage;
using Microsoft.WindowsAzure.Storage.Table;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.Tables
{
    public interface IJudgeTable : IAzureTable<JudgeEntity>
    {
        Task<IEnumerable<JudgeEntity>> ListByHackathonAsync(string hackathonName, CancellationToken cancellationToken = default);
    }

    public class JudgeTable : AzureTable<JudgeEntity>, IJudgeTable
    {
        public JudgeTable()
        {
            // UT only
        }

        public JudgeTable(CloudStorageAccount storageAccount, string tableName)
            : base(storageAccount, tableName)
        {
        }

        #region Task<IEnumerable<JudgeEntity>> ListByHackathonAsync(string hackathonName, CancellationToken cancellationToken = default);
        public async Task<IEnumerable<JudgeEntity>> ListByHackathonAsync(string hackathonName, CancellationToken cancellationToken = default)
        {
            List<JudgeEntity> list = new List<JudgeEntity>();

            var filter = TableQuery.GenerateFilterCondition(nameof(JudgeEntity.PartitionKey), QueryComparisons.Equal, hackathonName);
            TableQuery<JudgeEntity> query = new TableQuery<JudgeEntity>().Where(filter);

            await ExecuteQuerySegmentedAsync(query, (segment) =>
            {
                list.AddRange(segment);
            }, cancellationToken);

            return list;
        }
        #endregion
    }
}
