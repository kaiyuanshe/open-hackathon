using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.WindowsAzure.Storage;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.Tables
{
    public interface ITemplateTable : IAzureTable<TemplateEntity>
    {
    }

    public class TemplateTable : AzureTable<TemplateEntity>, ITemplateTable
    {
        public TemplateTable(CloudStorageAccount storageAccount, string tableName)
           : base(storageAccount, tableName)
        {
        }
    }
}
