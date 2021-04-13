using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Models
{
    public class TeamMember
    {
    }

    public enum TeamMemberRole
    {
        /// <summary>
        /// team admin who can approve/reject/add/remove team member.
        /// </summary>
        Admin,

        /// <summary>
        /// member of the team.
        /// </summary>
        Member,
    }

    /// <summary>
    /// Status of team member
    /// </summary>
    public enum TeamMemberStatus
    {
        /// <summary>
        /// Pending approval
        /// </summary>
        pendingApproval,

        /// <summary>
        /// Approved by team admin
        /// </summary>
        approved,

        /// <summary>
        /// Rejected by team admin
        /// </summary>
        rejected,
    }
}
