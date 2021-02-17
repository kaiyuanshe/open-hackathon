using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.WindowsAzure.Storage;

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
