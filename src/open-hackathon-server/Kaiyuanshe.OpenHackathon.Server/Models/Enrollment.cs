namespace Kaiyuanshe.OpenHackathon.Server.Models
{
    /// <summary>
    /// Status of the enrollment
    /// </summary>
    public class Enrollment
    {
        /// <summary>
        /// Status of enrollment.
        /// </summary>
        public EnrollmentStatus status { get; internal set; }
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