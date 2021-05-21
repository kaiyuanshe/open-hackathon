using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.WindowsAzure.Storage;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.Tables
{
    public interface IAwardTable : IAzureTable<AwardEntity>
    {
    }

    public class AwardTable : AzureTable<AwardEntity>, IAwardTable
    {
        public AwardTable(CloudStorageAccount storageAccount, string tableName)
            : base(storageAccount, tableName)
        {
        }
    }
}
