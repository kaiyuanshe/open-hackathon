using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.WindowsAzure.Storage;
using Microsoft.WindowsAzure.Storage.Table;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.Tables
{
    public interface IEnrollmentTable : IAzureTable<EnrollmentEntity>
    {
        /// <summary>
        /// List all enrollments by hackathon
        /// </summary>
        /// <param name="hackathonName">name of hackathon</param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<IEnumerable<EnrollmentEntity>> ListEnrollmentsAsync(string hackathonName, CancellationToken cancellationToken);
    }

    public class EnrollmentTable : AzureTable<EnrollmentEntity>, IEnrollmentTable
    {
        /// <summary>
        /// Test only constructor
        /// </summary>
        internal EnrollmentTable()
        {

        }

        public EnrollmentTable(CloudStorageAccount storageAccount, string tableName)
            : base(storageAccount, tableName)
        {
        }

        public async Task<IEnumerable<EnrollmentEntity>> ListEnrollmentsAsync(string name, CancellationToken cancellationToken)
        {
            var filter = TableQuery.GenerateFilterCondition(
                nameof(EnrollmentEntity.PartitionKey),
                QueryComparisons.Equal,
                name);
            TableQuery<EnrollmentEntity> query = new TableQuery<EnrollmentEntity>().Where(filter);
            List<EnrollmentEntity> results = new List<EnrollmentEntity>();
            await ExecuteQuerySegmentedAsync(query, segment =>
            {
                results.AddRange(segment);
            }, cancellationToken);
            return results;
        }
    }
}
