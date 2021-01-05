using Kaiyuanshe.OpenHackathon.Server.Storage.Tables;
using System;
using System.Collections.Generic;
using System.Text;

namespace Kaiyuanshe.OpenHackathon.Server.Storage
{
    public interface IStorageContext
    {
        IHackathonTable HackathonTable { get; }
    }


    public class StorageContext : IStorageContext
    {
        IStorageAccountProvider StorageAccountProvider { get; }

        public IHackathonTable HackathonTable { get; }

        public StorageContext(IStorageAccountProvider storageAccountProvider)
        {
            StorageAccountProvider = storageAccountProvider;

            // tables
            var storageAccount = storageAccountProvider.HackathonServerStorage;
            HackathonTable = new HackathonTable(storageAccount, TableNames.Hackathon);
        }
    }
}
