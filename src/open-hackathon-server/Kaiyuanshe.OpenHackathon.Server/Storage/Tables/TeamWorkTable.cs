using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.WindowsAzure.Storage;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.Tables
{
    public interface ITeamWorkTable : IAzureTable<TeamWorkEntity>
    {
    }

    public class TeamWorkTable : AzureTable<TeamWorkEntity>, ITeamWorkTable
    {
        public TeamWorkTable(CloudStorageAccount storageAccount, string tableName)
              : base(storageAccount, tableName)
        {
        }
    }
}
