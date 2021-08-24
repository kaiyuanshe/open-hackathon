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
    public interface IHackathonAdminTable : IAzureTable<HackathonAdminEntity>
    {
        /// <summary>
        /// Get platform-wide role of current user
        /// </summary>
        /// <param name="userId">user Id</param>
        /// <param name="cancellationToken"></param>
        /// <returns><seealso cref="EnrollmentEntity"/> or null.</returns>
        Task<HackathonAdminEntity> GetPlatformRole(string userId, CancellationToken cancellationToken);

        /// <summary>
        /// List all individual participants of a hackathon including admins, judges and contestents.
        /// </summary>
        /// <param name="hackathonName">name of hackathon. string.Empty for platform admin</param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<IEnumerable<HackathonAdminEntity>> ListByHackathonAsync(string hackathonName, CancellationToken cancellationToken);
    }

    public class HackathonAdminTable : AzureTable<HackathonAdminEntity>, IHackathonAdminTable
    {
        /// <summary>
        /// Test only constructor
        /// </summary>
        internal HackathonAdminTable()
        {

        }

        public HackathonAdminTable(CloudStorageAccount storageAccount, string tableName)
            : base(storageAccount, tableName)
        {
        }

        public async Task<HackathonAdminEntity> GetPlatformRole(string userId, CancellationToken cancellationToken)
        {
            return await RetrieveAsync(string.Empty, userId, cancellationToken);
        }

        public async Task<IEnumerable<HackathonAdminEntity>> ListByHackathonAsync(string name, CancellationToken cancellationToken)
        {
            var filter = TableQuery.GenerateFilterCondition(
                nameof(HackathonAdminEntity.PartitionKey),
                QueryComparisons.Equal,
                name);
            TableQuery<HackathonAdminEntity> query = new TableQuery<HackathonAdminEntity>().Where(filter);
            List<HackathonAdminEntity> results = new List<HackathonAdminEntity>();
            await ExecuteQuerySegmentedAsync(query, segment =>
            {
                results.AddRange(segment);
            }, cancellationToken);
            return results;
        }
    }
}
