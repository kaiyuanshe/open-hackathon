using Kaiyuanshe.OpenHackathon.Server.Helpers;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.WindowsAzure.Storage;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.Tables
{
    public interface IUserTokenTable : IAzureTable<UserTokenEntity>
    {
    }

    public class UserTokenTable : AzureTable<UserTokenEntity>, IUserTokenTable
    {
        public UserTokenTable(CloudStorageAccount storageAccount, string tableName) : base(storageAccount, tableName)
        {
        }
    }
}
