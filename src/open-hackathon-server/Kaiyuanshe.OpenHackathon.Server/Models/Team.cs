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
    public class Team : ModelBase
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
        /// Detailed user info of the creator
        /// </summary>
        public UserInfo creator { get; internal set; }
    }

    /// <summary>
    /// a list of teams and a optional nextLink for more results.
    /// </summary>
    public class TeamList : IResourceList<Team>
    {
        /// <summary>
        /// a list of teams
        /// </summary>
        public Team[] value { get; set; }

        /// <summary>
        ///  The URL the client should use to fetch the next page (per server side paging).
        ///  No more results if it's null or empty.
        /// </summary>
        public string nextLink { get; set; }
    }

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
    public class TeamMemberList : IResourceList<TeamMember>
    {
        /// <summary>
        /// a list of members
        /// </summary>
        public TeamMember[] value { get; set; }

        /// <summary>
        ///  The URL the client should use to fetch the next page (per server side paging).
        ///  No more results if it's null or empty.
        /// </summary>
        public string nextLink { get; set; }
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
