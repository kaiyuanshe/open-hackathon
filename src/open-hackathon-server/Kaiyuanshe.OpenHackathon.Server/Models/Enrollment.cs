using Newtonsoft.Json;
using System;

namespace Kaiyuanshe.OpenHackathon.Server.Models
{
    /// <summary>
    /// Status of the enrollment
    /// </summary>
    public class Enrollment
    {
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
        /// Status of enrollment.
        /// </summary>
        /// <example>Approved</example>
        public EnrollmentStatus status { get; internal set; }

        /// <summary>
        /// The timestamp when the enrollment submitted.
        /// </summary>
        /// <example>2008-01-14T04:33:35Z</example>
        public DateTime createdAt { get; internal set; }

        /// <summary>
        /// The timestamp when the enrollment submitted.
        /// </summary>
        /// <example>2008-01-14T04:33:35Z</example>
        public DateTime updatedAt { get; internal set; }
    }

    /// <summary>
    /// Status of the enrollment
    /// </summary>
    public enum EnrollmentStatus
    {
        /// <summary>
        /// Not enrolled
        /// </summary>
        None,

        /// <summary>
        /// Pending approval
        /// </summary>
        Pending,

        /// <summary>
        /// Approved by admin
        /// </summary>
        Approved,

        /// <summary>
        /// Rejected by admin
        /// </summary>
        Rejected,
    }
}