using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.WindowsAzure.Storage;
using System;
using System.Collections.Generic;
using System.Text;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.Tables
{
    public interface IHackathonTable : IAzureTable<HackathonEntity>
    {

    }

    public class HackathonTable : AzureTable<HackathonEntity>, IHackathonTable
    {
        public HackathonTable(CloudStorageAccount storageAccount, string tableName)
            : base(storageAccount, tableName)
        {

        }
    }
}
