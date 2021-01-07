using Kaiyuanshe.OpenHackathon.Server.Models.Enums;
using Microsoft.WindowsAzure.Storage.Table;
using System;
using System.Collections.Generic;
using System.Text;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.Entities
{
    /// <summary>
    /// Hackathons.
    /// </summary>
    public class HackathonEntity : AdvancedTableEntity
    {
        /// <summary>
        /// Id of Hackathon. Auto-generated, the same as PartitionKey
        /// </summary>
        [IgnoreProperty]
        public string Id
        {
            get
            {
                return PartitionKey;
            }
        }

        public string Name { get; set; }
        /// <summary>
        /// A short sentence for advertisement
        /// </summary>
        public string Ribbon { get; set; }
        public string Summary { get; set; }
        /// <summary>
        /// Detailed description. Usually rich-text html
        /// </summary>
        public string Description { get; set; }
        public string Location { get; set; }
        /// <summary>
        /// Uploaded pictures for display as banners
        /// </summary>
        public string[] Banners { get; set; }
        public HackathonStatus Status { get; set; }
        /// <summary>
        /// Id of User who creates this hackathon
        /// </summary>
        public string CreatedBy { get; set; }
        /// <summary>
        /// Maximum allowed participant
        /// </summary>
        public int MaxEnrollment { get; set; }
        /// <summary>
        /// whether or not user registration needs admin's manual approval
        /// </summary>
        public bool AutoApprove { get; set; }
        /// <summary>
        /// an array of organizer's Id
        /// </summary>
        public string[] Tags { get; set; }
        public DateTime CreatedTime { get; set; }
        public DateTime EventStartTime { get; set; }
        public DateTime EventEndTime { get; set; }
        public DateTime RegisterStartTime { get; set; }
        public DateTime RegisterEndTime { get; set; }
        public DateTime JudgeStartTime { get; set; }
        public DateTime JudgeEndTime { get; set; }
        public DateTime ArchiveTime { get; set; }
    }
}
