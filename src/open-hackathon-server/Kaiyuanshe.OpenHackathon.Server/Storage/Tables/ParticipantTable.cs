using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.WindowsAzure.Storage;
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
    }

    public class ParticipantTable : AzureTable<ParticipantEntity>, IParticipantTable
    {
        public ParticipantTable(CloudStorageAccount storageAccount, string tableName)
            : base(storageAccount, tableName)
        {
        }

        public async Task<ParticipantEntity> GetPlatformRole(string userId, CancellationToken cancellationToken)
        {
            return await RetrieveAsync(string.Empty, userId, cancellationToken);
        }
    }
}
