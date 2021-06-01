using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.WindowsAzure.Storage;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.Tables
{
    public interface IAwardAssignmentTable : IAzureTable<AwardAssignmentEntity>
    {
    }

    public class AwardAssignmentTable : AzureTable<AwardAssignmentEntity>, IAwardAssignmentTable
    {
        public AwardAssignmentTable(CloudStorageAccount storageAccount, string tableName)
            : base(storageAccount, tableName)
        {
        }
    }
}
