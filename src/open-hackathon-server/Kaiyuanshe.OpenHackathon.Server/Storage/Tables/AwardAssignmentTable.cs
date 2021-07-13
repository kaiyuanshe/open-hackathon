using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.WindowsAzure.Storage;
using Microsoft.WindowsAzure.Storage.Table;
using System.Collections;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.Tables
{
    public interface IAwardAssignmentTable : IAzureTable<AwardAssignmentEntity>
    {
        Task<IEnumerable<AwardAssignmentEntity>> ListByHackathonAsync(string hackathonName, CancellationToken cancellationToken = default);

        Task<IEnumerable<AwardAssignmentEntity>> ListByAwardAsync(string hackathonName, string awardId, CancellationToken cancellationToken = default);

        Task<IEnumerable<AwardAssignmentEntity>> ListByAssigneeAsync(string hackathonName, string assigneeId, CancellationToken cancellationToken = default);

    }

    public class AwardAssignmentTable : AzureTable<AwardAssignmentEntity>, IAwardAssignmentTable
    {
        public AwardAssignmentTable(CloudStorageAccount storageAccount, string tableName)
            : base(storageAccount, tableName)
        {
        }

        internal AwardAssignmentTable()
        {
            // UT only
        }

        #region ListByHackathonAsync
        public async Task<IEnumerable<AwardAssignmentEntity>> ListByHackathonAsync(string hackathonName, CancellationToken cancellationToken = default)
        {
            List<AwardAssignmentEntity> list = new List<AwardAssignmentEntity>();

            var filter = TableQuery.GenerateFilterCondition(
                nameof(AwardAssignmentEntity.PartitionKey),
                QueryComparisons.Equal,
                hackathonName);

            TableQuery<AwardAssignmentEntity> query = new TableQuery<AwardAssignmentEntity>().Where(filter);
            await ExecuteQuerySegmentedAsync(query, (segment) =>
            {
                list.AddRange(segment);
            }, cancellationToken);

            return list;
        }
        #endregion

        #region ListByAwardAsync
        public async Task<IEnumerable<AwardAssignmentEntity>> ListByAwardAsync(string hackathonName, string awardId, CancellationToken cancellationToken = default)
        {
            List<AwardAssignmentEntity> list = new List<AwardAssignmentEntity>();

            var hackathonNameFilter = TableQuery.GenerateFilterCondition(
                nameof(AwardAssignmentEntity.PartitionKey),
                QueryComparisons.Equal,
                hackathonName);
            var awardIdFilter = TableQuery.GenerateFilterCondition(
                nameof(AwardAssignmentEntity.AwardId),
                QueryComparisons.Equal,
                awardId);
            var filter = TableQueryHelper.And(hackathonNameFilter, awardIdFilter);

            TableQuery<AwardAssignmentEntity> query = new TableQuery<AwardAssignmentEntity>().Where(filter);
            await ExecuteQuerySegmentedAsync(query, (segment) =>
            {
                list.AddRange(segment);
            }, cancellationToken);

            return list;
        }
        #endregion

        #region ListByAssigneeAsync
        public async Task<IEnumerable<AwardAssignmentEntity>> ListByAssigneeAsync(string hackathonName, string assigneeId, CancellationToken cancellationToken = default)
        {
            List<AwardAssignmentEntity> list = new List<AwardAssignmentEntity>();

            var hackathonNameFilter = TableQuery.GenerateFilterCondition(
                nameof(AwardAssignmentEntity.PartitionKey),
                QueryComparisons.Equal,
                hackathonName);
            var assigneeIdFilter = TableQuery.GenerateFilterCondition(
                nameof(AwardAssignmentEntity.AssigneeId),
                QueryComparisons.Equal,
                assigneeId);
            var filter = TableQueryHelper.And(hackathonNameFilter, assigneeIdFilter);

            TableQuery<AwardAssignmentEntity> query = new TableQuery<AwardAssignmentEntity>().Where(filter);
            await ExecuteQuerySegmentedAsync(query, (segment) =>
            {
                list.AddRange(segment);
            }, cancellationToken);

            return list;
        }
        #endregion
    }
}
