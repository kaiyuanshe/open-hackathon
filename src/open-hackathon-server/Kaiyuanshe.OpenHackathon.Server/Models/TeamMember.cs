using System.ComponentModel.DataAnnotations;

namespace Kaiyuanshe.OpenHackathon.Server.Models
{
    /// <summary>
    /// Represent a member in a team
    /// </summary>
    public class TeamMember : ModelBase
    {
        /// <summary>
        /// name of hackathon
        /// </summary>
        /// <example>foo</example>
        public string hackathonName { get; internal set; }

        /// <summary>
        /// Unique id of the team.
        /// </summary>
        /// <example>d1e40c38-cc2a-445f-9eab-60c253256c57</example>
        public string teamId { get; internal set; }

        /// <summary>
        /// id of user
        /// </summary>
        /// <example>1</example>
        public string userId { get; internal set; }

        /// <summary>
        /// Detailed user info of the member
        /// </summary>
        public UserInfo user { get; internal set; }

        /// <summary>
        /// description of the member.
        /// </summary>
        /// <example>Java expert in team, working on backend.</example>
        [MaxLength(512)]
        public string description { get; set; }

        /// <summary>
        /// Role in the team
        /// </summary>
        /// <example>admin</example>
        public TeamMemberRole? role { get; set; }

        /// <summary>
        /// Status of the membership
        /// </summary>
        /// <example>approved</example>
        public TeamMemberStatus status { get; internal set; }
    }

    /// <summary>
    /// a list of team members and a optional nextLink for more results.
    /// </summary>
    public class TeamMemberList : ResourceList<TeamMember>
    {
        /// <summary>
        /// a list of members
        /// </summary>
        public override TeamMember[] value { get; set; }
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
    }
}
