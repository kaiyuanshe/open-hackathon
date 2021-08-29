using Kaiyuanshe.OpenHackathon.Server.Models;
using Microsoft.WindowsAzure.Storage.Table;
using System;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.Entities
{
    /// <summary>
    /// Represents a team member.
    /// 
    /// PK: Hackathon name.
    /// RK: UserId.
    /// </summary>
    public class TeamMemberEntity : AdvancedTableEntity
    {
        /// <summary>
        /// PartitionKey.
        /// </summary>
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

        public string TeamId { get; set; }

        public string Description { get; set; }

        public TeamMemberRole Role { get; set; }

        public TeamMemberStatus Status { get; set; }
    }
}
