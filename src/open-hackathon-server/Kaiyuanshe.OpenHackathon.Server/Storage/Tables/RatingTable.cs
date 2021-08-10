using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.WindowsAzure.Storage;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.Tables
{
    public interface IRatingTable : IAzureTable<RatingEntity>
    {
    }

    public class RatingTable : AzureTable<RatingEntity>, IRatingTable
    {
        public RatingTable(CloudStorageAccount storageAccount, string tableName)
           : base(storageAccount, tableName)
        {
        }
    }
}
