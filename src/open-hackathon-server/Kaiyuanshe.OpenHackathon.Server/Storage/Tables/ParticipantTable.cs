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
    public interface IParticipantTable : IAzureTable<ParticipantEntity>
    {
        /// <summary>
        /// Get platform-wide role of current user
        /// </summary>
        /// <param name="userId">user Id</param>
        /// <param name="cancellationToken"></param>
        /// <returns><seealso cref="ParticipantEntity"/> or null.</returns>
        Task<ParticipantEntity> GetPlatformRole(string userId, CancellationToken cancellationToken);

        /// <summary>
        /// List all individual participants of a hackathon including admins, judges and contestents.
        /// </summary>
        /// <param name="hackathonName">name of hackathon</param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<IEnumerable<ParticipantEntity>> ListParticipantsByHackathonAsync(string hackathonName, CancellationToken cancellationToken);
    }

    public class ParticipantTable : AzureTable<ParticipantEntity>, IParticipantTable
    {
        /// <summary>
        /// Test only constructor
        /// </summary>
        internal ParticipantTable()
        {

        }

        public ParticipantTable(CloudStorageAccount storageAccount, string tableName)
            : base(storageAccount, tableName)
        {
        }

        public async Task<ParticipantEntity> GetPlatformRole(string userId, CancellationToken cancellationToken)
        {
            return await RetrieveAsync(string.Empty, userId, cancellationToken);
        }

        public async Task<IEnumerable<ParticipantEntity>> ListParticipantsByHackathonAsync(string name, CancellationToken cancellationToken)
        {
            var filter = TableQuery.GenerateFilterCondition(
                nameof(ParticipantEntity.PartitionKey),
                QueryComparisons.Equal,
                name);
            TableQuery<ParticipantEntity> query = new TableQuery<ParticipantEntity>().Where(filter);
            List<ParticipantEntity> results = new List<ParticipantEntity>();
            await ExecuteQuerySegmentedAsync(query, segment =>
            {
                results.AddRange(segment);
            }, cancellationToken);
            return results;
        }
    }
}
