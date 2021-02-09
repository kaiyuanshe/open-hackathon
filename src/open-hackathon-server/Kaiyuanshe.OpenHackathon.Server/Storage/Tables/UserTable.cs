using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.WindowsAzure.Storage;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.Tables
{
    public interface IUserTable : IAzureTable<UserEntity>
    {
        Task<UserEntity> GetUserEntityByIdAsync(string id, CancellationToken cancellationToken = default);

    }

    public class UserTable : AzureTable<UserEntity>, IUserTable
    {
        public UserTable(CloudStorageAccount storageAccount, string tableName) : base(storageAccount, tableName)
        {
        }

        public async Task<UserEntity> GetUserEntityByIdAsync(string id, CancellationToken cancellationToken = default)
        {
            return await RetrieveAsync(id.ToLower(), string.Empty, cancellationToken);
        }
    }
}
