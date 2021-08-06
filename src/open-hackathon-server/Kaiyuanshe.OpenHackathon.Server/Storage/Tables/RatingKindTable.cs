using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.WindowsAzure.Storage;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.Tables
{
    public interface IRatingKindTable : IAzureTable<RatingKindEntity>
    { }

    public class RatingKindTable : AzureTable<RatingKindEntity>, IRatingKindTable
    {
        public RatingKindTable(CloudStorageAccount storageAccount, string tableName)
          : base(storageAccount, tableName)
        {
        }
    }
}
