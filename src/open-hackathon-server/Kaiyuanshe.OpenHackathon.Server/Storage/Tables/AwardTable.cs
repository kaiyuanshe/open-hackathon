using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.WindowsAzure.Storage;
using Microsoft.WindowsAzure.Storage.Table;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.Tables
{
    public interface IAwardTable : IAzureTable<AwardEntity>
    {
        Task<IEnumerable<AwardEntity>> ListAllAwardsAsync(string hackathonName, CancellationToken cancellationToken = default);
    }

    public class AwardTable : AzureTable<AwardEntity>, IAwardTable
    {
        /// <summary>
        /// Test only constructor
        /// </summary>
        internal AwardTable()
        {

        }

        public AwardTable(CloudStorageAccount storageAccount, string tableName)
            : base(storageAccount, tableName)
        {
        }

        #region ListAllAwardsAsync
        public async Task<IEnumerable<AwardEntity>> ListAllAwardsAsync(string hackathonName, CancellationToken cancellationToken = default)
        {
            List<AwardEntity> list = new List<AwardEntity>();

            var filter = TableQuery.GenerateFilterCondition(
                           nameof(AwardEntity.PartitionKey),
                           QueryComparisons.Equal,
                           hackathonName);

            TableQuery<AwardEntity> query = new TableQuery<AwardEntity>().Where(filter);
            await ExecuteQuerySegmentedAsync(query, (segment) =>
            {
                list.AddRange(segment);
            }, cancellationToken);

            return list;
        }
        #endregion
    }
}
