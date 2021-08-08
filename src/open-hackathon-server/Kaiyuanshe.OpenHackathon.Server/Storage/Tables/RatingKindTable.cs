using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.WindowsAzure.Storage;
using Microsoft.WindowsAzure.Storage.Table;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.Tables
{
    public interface IRatingKindTable : IAzureTable<RatingKindEntity>
    {
        Task<IEnumerable<RatingKindEntity>> ListRatingKindsAsync(string hackathonName, CancellationToken cancellationToken = default);
    }

    public class RatingKindTable : AzureTable<RatingKindEntity>, IRatingKindTable
    {
        // UT only
        public RatingKindTable()
        {
        }

        public RatingKindTable(CloudStorageAccount storageAccount, string tableName)
          : base(storageAccount, tableName)
        {
        }

        #region Task<IEnumerable<RatingKindEntity>> ListRatingKindsAsync(string hackathonName, CancellationToken cancellationToken = default)
        public async Task<IEnumerable<RatingKindEntity>> ListRatingKindsAsync(string hackathonName, CancellationToken cancellationToken = default)
        {
            List<RatingKindEntity> list = new List<RatingKindEntity>();

            var filter = TableQuery.GenerateFilterCondition(
                           nameof(RatingKindEntity.PartitionKey),
                           QueryComparisons.Equal,
                           hackathonName);

            TableQuery<RatingKindEntity> query = new TableQuery<RatingKindEntity>().Where(filter);
            await ExecuteQuerySegmentedAsync(query, (segment) =>
            {
                list.AddRange(segment);
            }, cancellationToken);

            return list;
        }
        #endregion
    }
}
