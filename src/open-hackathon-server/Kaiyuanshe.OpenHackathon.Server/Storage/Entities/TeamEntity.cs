using Microsoft.WindowsAzure.Storage.Table;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.Entities
{
    /// <summary>
    /// entity for team information
    /// 
    /// PK: hackathon name
    /// RK: auto-generated GUID
    /// </summary>
    public class TeamEntity : AdvancedTableEntity
    {
        /// <summary>
        /// name of Hackathon
        /// </summary>
        [IgnoreProperty]
        public string HackathonName { get; }

        /// <summary>
        /// team display name
        /// </summary>
        public string DisplayName { get; set; }

        /// <summary>
        /// description about the team
        /// </summary>
        public string Description { get; set; }

        /// <summary>
        /// whether or not auto approve team joining request.
        /// </summary>
        public bool AutoApprove { get; set; }

        /// <summary>
        /// the id of user who creates the team
        /// </summary>
        public string CreatorId { get; set; }

        /// <summary>
        /// datetime when the team is created
        /// </summary>
        public DateTime CreatedAt { get; set; }
    }
}
