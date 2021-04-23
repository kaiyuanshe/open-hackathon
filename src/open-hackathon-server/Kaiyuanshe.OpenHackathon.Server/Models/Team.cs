using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Models
{
    /// <summary>
    /// Describes a team
    /// </summary>
    public class Team
    {
        /// <summary>
        /// name of Hackathon
        /// </summary>
        /// <example>foo</example>
        public string hackathonName { get; internal set; }

        /// <summary>
        /// auto-generated id of the team.
        /// </summary>
        /// <example>d1e40c38-cc2a-445f-9eab-60c253256c57</example>
        public string id { get; internal set; }

        /// <summary>
        /// team display name.
        /// </summary>
        /// <example>My Team</example>
        [Required]
        [MaxLength(128)]
        public string displayName { get; set; }

        /// <summary>
        /// description about the team
        /// </summary>
        /// <example>my fantastic team, the best team ever.</example>
        [MaxLength(512)]
        public string description { get; set; }

        /// <summary>
        /// whether or not auto approve team joining request. false by default.
        /// </summary>
        /// <example>true</example>
        public bool? autoApprove { get; set; }

        /// <summary>
        /// the id of user who creates the team
        /// </summary>
        /// <example>1</example>
        public string creatorId { get; internal set; }

        /// <summary>
        /// datetime when the team is created
        /// </summary>
        /// <example>2008-01-14T04:33:35Z</example>
        public DateTime createdAt { get; internal set; }

        /// <summary>
        /// The timestamp when the team is updated.
        /// </summary>
        /// <example>2008-01-14T04:33:35Z</example>
        public DateTime updatedAt { get; internal set; }
    }

    /// <summary>
    /// Represent a member in a team
    /// </summary>
    public class TeamMember
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
        /// description of the member.
        /// </summary>
        /// <example>Java expert in team, working on backend.</example>
        [MaxLength(512)]
        public string description { get; set; }

        /// <summary>
        /// Role in the team
        /// </summary>
        /// <example>admin</example>
        public TeamMemberRole role { get; internal set; }

        /// <summary>
        /// Status of the membership
        /// </summary>
        /// <example>approved</example>
        public TeamMemberStatus status { get; internal set; }

        /// <summary>
        /// datetime when the member joons the team
        /// </summary>
        /// <example>2008-01-14T04:33:35Z</example>
        public DateTime createdAt { get; internal set; }

        /// <summary>
        /// The timestamp when the membership updated
        /// </summary>
        /// <example>2008-01-14T04:33:35Z</example>
        public DateTime updatedAt { get; internal set; }
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
