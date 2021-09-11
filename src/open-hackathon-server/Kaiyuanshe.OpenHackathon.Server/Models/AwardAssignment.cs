using Kaiyuanshe.OpenHackathon.Server.Models.Validations;
using System;
using System.ComponentModel.DataAnnotations;

namespace Kaiyuanshe.OpenHackathon.Server.Models
{
    /// <summary>
    /// represents an assignment. An award can be assigned to multiple teams or individuals.
    /// </summary>
    public class AwardAssignment : ModelBase
    {
        /// <summary>
        /// name of hackathon
        /// </summary>
        /// <example>foo</example>
        public string hackathonName { get; internal set; }

        /// <summary>
        /// Auto-generated Guid.
        /// </summary>
        /// <example>d1e40c38-cc2a-445f-9eab-60c253256c57</example>
        public string assignmentId { get; internal set; }

        /// <summary>
        /// id of the assignee. userId if award target is individual, or teamId if award target is team.
        /// </summary>
        /// <example>d1e40c38-cc2a-445f-9eab-60c253256c57</example>
        [RequiredIfPut]
        [MaxLength(128)]
        public string assigneeId { get; set; }

        /// <summary>
        /// awared user. It's null if the award is assigned to a team.
        /// </summary>
        public UserInfo user { get; internal set; }

        /// <summary>
        /// awarded team. It's null if the award is assigned to an individual user.
        /// </summary>
        public Team team { get; internal set; }

        /// <summary>
        /// id of the award.
        /// </summary>
        /// <example>d1e40c38-cc2a-445f-9eab-60c253256c57</example>
        [Guid]
        public string awardId { get; internal set; }

        /// <summary>
        /// description of the assignment
        /// </summary>
        /// <example>amazing team</example>
        [MaxLength(256)]
        public string description { get; set; }
    }


    /// <summary>
    /// a list of award assignments
    /// </summary>
    public class AwardAssignmentList : ResourceList<AwardAssignment>
    {
        /// <summary>
        /// a list of assignments
        /// </summary>
        public override AwardAssignment[] value { get; set; }
    }
}
