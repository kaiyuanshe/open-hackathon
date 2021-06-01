using Microsoft.WindowsAzure.Storage.Table;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.Entities
{
    /// <summary>
    /// entity for assignment info for an award
    /// 
    /// PK: Hackathon name
    /// RK: target id. Auto-generated GUID.
    /// </summary>
    public class AwardAssignmentEntity : AdvancedTableEntity
    {
        /// <summary>
        /// name of hackathon
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
        public string AssignmentId
        {
            get
            {
                return RowKey;
            }
        }

        /// <summary>
        /// id of the assignee. userId(if award.Target is individual) or teamId(if award.Target is team).
        /// </summary>
        public string Assignee { get; set; }

        public string AwardId { get; set; }

        public string Description { get; set; }
    }
}
