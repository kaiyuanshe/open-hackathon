﻿using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.WindowsAzure.Storage;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.Tables
{
    public interface IEnrollmentTable : IAzureTable<EnrollmentEntity>
    {
    }

    public class EnrollmentTable : AzureTable<EnrollmentEntity>, IEnrollmentTable
    {
        /// <summary>
        /// Test only constructor
        /// </summary>
        internal EnrollmentTable()
        {

        }

        public EnrollmentTable(CloudStorageAccount storageAccount, string tableName)
            : base(storageAccount, tableName)
        {
        }
    }
}
