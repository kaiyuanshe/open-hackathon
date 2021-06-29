using Kaiyuanshe.OpenHackathon.Server.Models;
using Microsoft.WindowsAzure.Storage.Table;
using System;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.Entities
{
    /// <summary>
    /// Represents a hackathon participant. Could be admin, organizer, partner, judge and so on.
    /// 
    /// PK: hackathon Name. 
    /// RK: user Id.
    /// 
    /// PK might be string.Empty for PlatformAdministrator.
    /// </summary>
    public class EnrollmentEntity : AdvancedTableEntity
    {
        [IgnoreProperty]
        public string HackathonName
        {
            get
            {
                return PartitionKey;
            }
        }

        [IgnoreProperty]
        public string UserId
        {
            get
            {
                return RowKey;
            }
        }

        public EnrollmentStatus Status { get; set; }

        [ConvertableEntityProperty]
        public Extension[] Extensions { get; set; }
    }
}
