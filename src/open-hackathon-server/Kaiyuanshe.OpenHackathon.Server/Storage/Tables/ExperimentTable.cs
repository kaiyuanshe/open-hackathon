using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.WindowsAzure.Storage;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.Tables
{
    public interface IExperimentTable : IAzureTable<ExperimentEntity>
    {
    }

    public class ExperimentTable : AzureTable<ExperimentEntity>, IExperimentTable
    {
        public ExperimentTable(CloudStorageAccount storageAccount, string tableName)
           : base(storageAccount, tableName)
        {
        }
    }
}
