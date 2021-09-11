using Kaiyuanshe.OpenHackathon.Server.Models.Validations;
using System;
using System.ComponentModel.DataAnnotations;

namespace Kaiyuanshe.OpenHackathon.Server.Models
{
    /// <summary>
    /// Status of the enrollment
    /// </summary>
    public class Enrollment : ModelBase
    {
        public const int MaxExtensions = 10;

        /// <summary>
        /// name of hackathon
        /// </summary>
        /// <example>foo</example>
        public string hackathonName { get; internal set; }

        /// <summary>
        /// id of user
        /// </summary>
        /// <example>1</example>
        public string userId { get; internal set; }

        /// <summary>
        /// detailed info of the enrolled user. The info is from Authing.
        /// </summary>
        public UserInfo user { get; internal set; }

        /// <summary>
        /// Status of enrollment.
        /// </summary>
        /// <example>approved</example>
        public EnrollmentStatus status { get; internal set; }

        /// <summary>
        /// Extra properties. A maximum of 10 extensions are allowed. 
        /// `name`(case-sensitive) must be unique. If not unique, the last item with same name will be saved, others are ignored.
        /// </summary>
        [MaxLength(MaxExtensions)]
        public Extension[] extensions { get; set; }
    }

    /// <summary>
    /// Status of the enrollment
    /// </summary>
    public enum EnrollmentStatus
    {
        /// <summary>
        /// Not enrolled
        /// </summary>
        none,

        /// <summary>
        /// Pending approval
        /// </summary>
        pendingApproval,

        /// <summary>
        /// Approved by admin
        /// </summary>
        approved,

        /// <summary>
        /// Rejected by admin
        /// </summary>
        rejected,
    }

    /// <summary>
    /// a list of enrollment
    /// </summary>
    public class EnrollmentList : ResourceList<Enrollment>
    {
        /// <summary>
        /// a list of enrollment
        /// </summary>
        public override Enrollment[] value { get; set; }
    }
}