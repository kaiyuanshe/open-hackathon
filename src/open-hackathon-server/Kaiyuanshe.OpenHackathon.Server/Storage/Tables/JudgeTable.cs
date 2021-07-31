using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.WindowsAzure.Storage;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.Tables
{
    public interface IJudgeTable : IAzureTable<JudgeEntity>
    {
    }

    public class JudgeTable : AzureTable<JudgeEntity>, IJudgeTable
    {
        public JudgeTable(CloudStorageAccount storageAccount, string tableName)
            : base(storageAccount, tableName)
        {
        }
    }
}
