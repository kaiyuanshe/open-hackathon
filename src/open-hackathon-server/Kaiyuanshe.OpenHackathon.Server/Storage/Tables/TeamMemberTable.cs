using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.WindowsAzure.Storage;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.Tables
{
    public interface ITeamMemberTable : IAzureTable<TeamMemberEntity>
    {
    }

    public class TeamMemberTable : AzureTable<TeamMemberEntity>, ITeamMemberTable
    {
        public TeamMemberTable(CloudStorageAccount storageAccount, string tableName)
              : base(storageAccount, tableName)
        {
        }
    }
}
