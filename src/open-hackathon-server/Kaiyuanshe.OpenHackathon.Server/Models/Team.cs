using System.ComponentModel.DataAnnotations;

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

        /// <summary>
        /// count of members, including members pending approval.
        /// </summary>
        public int  membersCount { get; set; }
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
}
