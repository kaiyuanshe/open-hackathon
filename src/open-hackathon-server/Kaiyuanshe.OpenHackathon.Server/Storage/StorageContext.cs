﻿using Kaiyuanshe.OpenHackathon.Server.Storage.Tables;
using System;
using System.Collections.Generic;
using System.Runtime.CompilerServices;
using System.Text;

namespace Kaiyuanshe.OpenHackathon.Server.Storage
{
    public interface IStorageContext
    {
        IHackathonTable HackathonTable { get; }
        IHackathonAdminTable HackathonAdminTable { get; }
        IEnrollmentTable EnrollmentTable { get; }
        IUserTable UserTable { get; }
        IUserTokenTable UserTokenTable { get; }
    }


    public class StorageContext : IStorageContext
    {
        IStorageAccountProvider StorageAccountProvider { get; }

        public IEnrollmentTable EnrollmentTable { get; }
        public IHackathonAdminTable HackathonAdminTable { get; }
        public IHackathonTable HackathonTable { get; }
        public ITeamTable TeamTable { get; }
        public IUserTable UserTable { get; }
        public IUserTokenTable UserTokenTable { get; }

        public StorageContext(IStorageAccountProvider storageAccountProvider)
        {
            StorageAccountProvider = storageAccountProvider;

            // tables
            var storageAccount = storageAccountProvider.HackathonServerStorage;
            EnrollmentTable = new EnrollmentTable(storageAccount, TableNames.Enrollment);
            HackathonAdminTable = new HackathonAdminTable(storageAccount, TableNames.HackathonAdmin);
            HackathonTable = new HackathonTable(storageAccount, TableNames.Hackathon);
            TeamTable = new TeamTable(storageAccount, TableNames.Team);
            UserTable = new UserTable(storageAccount, TableNames.User);
            UserTokenTable = new UserTokenTable(storageAccount, TableNames.UserToken);
        }
    }
}
