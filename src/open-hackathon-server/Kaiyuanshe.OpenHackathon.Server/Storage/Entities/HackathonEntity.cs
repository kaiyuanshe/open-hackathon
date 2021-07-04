using Kaiyuanshe.OpenHackathon.Server.Models;
using Microsoft.WindowsAzure.Storage.Table;
using System;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.Entities
{
    /// <summary>
    /// Hackathons. 
    /// PartitionKey: auto-generated string. 
    /// RowKey: string.Empty
    /// </summary>
    public class HackathonEntity : AdvancedTableEntity
    {
        /// <summary>
        /// name of Hackathon. the same as PartitionKey
        /// </summary>
        [IgnoreProperty]
        public string Name
        {
            get
            {
                return PartitionKey;
            }
        }
        public string DisplayName { get; set; }
        /// <summary>
        /// A short sentence for advertisement
        /// </summary>
        public string Ribbon { get; set; }
        public string Summary { get; set; }
        /// <summary>
        /// Detailed description. Usually rich-text html
        /// </summary>
        public string Detail { get; set; }
        public string Location { get; set; }
        /// <summary>
        /// Uploaded pictures for display as banners
        /// </summary>
        [ConvertableEntityProperty]
        public PictureInfo[] Banners { get; set; }
        public HackathonStatus Status { get; set; }

        public bool ReadOnly { get; set; }

        /// <summary>
        /// Id of User who creates this hackathon. PartitionKey of Users table
        /// </summary>
        public string CreatorId { get; set; }

        /// <summary>
        /// current enrollment
        /// </summary>
        public int Enrollment { get; set; } = 0;

        /// <summary>
        /// Maximum allowed participant. 0 or negative number means unlimited.
        /// </summary>
        public int MaxEnrollment { get; set; } = 0;

        /// <summary>
        /// whether or not user registration needs admin's manual approval
        /// </summary>
        public bool AutoApprove { get; set; }
        [ConvertableEntityProperty]
        public string[] Tags { get; set; }
        public DateTime? EventStartedAt { get; set; }
        public DateTime? EventEndedAt { get; set; }
        public DateTime? EnrollmentStartedAt { get; set; }
        public DateTime? EnrollmentEndedAt { get; set; }
        public DateTime? JudgeStartedAt { get; set; }
        public DateTime? JudgeEndedAt { get; set; }

        public bool IsOnline()
        {
            return Status == HackathonStatus.online;
        }

        class ValiateOptions { }


    }
}
