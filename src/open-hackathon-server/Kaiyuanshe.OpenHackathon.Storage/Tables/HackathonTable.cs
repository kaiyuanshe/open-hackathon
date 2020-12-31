using AzSignalR.Storage;
using Kaiyuanshe.OpenHackathon.Storage.Entities;
using Microsoft.WindowsAzure.Storage;
using System;
using System.Collections.Generic;
using System.Text;

namespace Kaiyuanshe.OpenHackathon.Storage.Tables
{
    public interface IHackathonTable
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
