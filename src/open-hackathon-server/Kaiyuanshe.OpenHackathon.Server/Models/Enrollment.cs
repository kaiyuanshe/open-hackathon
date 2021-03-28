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
        /// <example>approved</example>
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
        none,

        /// <summary>
        /// Pending approval
        /// </summary>
        pending,

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
    public class EnrollmentList : IResourceList<Enrollment>
    {
        /// <summary>
        /// a list of enrollment
        /// </summary>
        public Enrollment[] value { get; set; }

        /// <summary>
        ///  The URL the client should use to fetch the next page (per server side paging).
        ///  No more results if it's null or empty.
        /// </summary>
        public string nextLink { get; set; }
    }
}