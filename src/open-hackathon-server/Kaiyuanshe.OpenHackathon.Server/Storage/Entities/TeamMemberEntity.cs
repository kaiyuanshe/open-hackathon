using Kaiyuanshe.OpenHackathon.Server.Models;
using Microsoft.WindowsAzure.Storage.Table;
using System;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.Entities
{
    /// <summary>
    /// Represents a team member.
    /// 
    /// PK: Id(RK) of TeamEntity.
    /// RK: UserId.
    /// </summary>
    public class TeamMemberEntity : AdvancedTableEntity
    {
        [IgnoreProperty]
        public string TeamId
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

        public string HackathonName { get; set; }

        public string Description { get; set; }

        public TeamMemberRole Role { get; set; }

        public TeamMemberStatus Status { get; set; }

        /// <summary>
        /// datetime when the member joons the team
        /// </summary>
        public DateTime CreatedAt { get; set; }
    }
}
