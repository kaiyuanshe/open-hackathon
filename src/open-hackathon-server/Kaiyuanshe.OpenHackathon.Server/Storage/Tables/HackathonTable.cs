using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.WindowsAzure.Storage;
using Microsoft.WindowsAzure.Storage.Table;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using System.Linq;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.Tables
{
    public interface IHackathonTable : IAzureTable<HackathonEntity>
    {
        Task<Dictionary<string, HackathonEntity>> ListAllHackathonsAsync(CancellationToken cancellationToken);
    }

    public class HackathonTable : AzureTable<HackathonEntity>, IHackathonTable
    {
        public HackathonTable(CloudStorageAccount storageAccount, string tableName)
            : base(storageAccount, tableName)
        {

        }

        public async Task<Dictionary<string, HackathonEntity>> ListAllHackathonsAsync(CancellationToken cancellationToken)
        {
            List<HackathonEntity> list = new List<HackathonEntity>();

            TableQuery<HackathonEntity> query = new TableQuery<HackathonEntity>();
            TableContinuationToken tableContinuationToken = null;
            do
            {
                var segment = await ExecuteQuerySegmentedAsync(query, tableContinuationToken, cancellationToken);
                list.AddRange(segment);
                tableContinuationToken = segment.ContinuationToken;
            } while (tableContinuationToken != null);

            return list.ToDictionary(h => h.Name, h => h);
        }
    }
}
