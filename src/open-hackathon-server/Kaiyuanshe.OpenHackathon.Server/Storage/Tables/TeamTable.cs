using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.WindowsAzure.Storage;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.Tables
{
    public interface ITeamTable : IAzureTable<TeamEntity>
    {
    }

    public class TeamTable : AzureTable<TeamEntity>, ITeamTable
    {
        public TeamTable(CloudStorageAccount storageAccount, string tableName)
           : base(storageAccount, tableName)
        {
        }
    }
}
