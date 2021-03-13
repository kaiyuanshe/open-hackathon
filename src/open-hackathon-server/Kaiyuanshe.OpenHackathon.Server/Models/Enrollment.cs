namespace Kaiyuanshe.OpenHackathon.Server.Models
{
    /// <summary>
    /// Status of the enrollment
    /// </summary>
    public enum EnrollmentStatus
    {
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