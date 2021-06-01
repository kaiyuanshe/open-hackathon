using Kaiyuanshe.OpenHackathon.Server.Models.Validations;
using System;
using System.ComponentModel.DataAnnotations;

namespace Kaiyuanshe.OpenHackathon.Server.Models
{
    /// <summary>
    /// represents an assignment. An award can be assigned to multiple teams or individuals.
    /// </summary>
    public class AwardAssignment
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
        [Required]
        [MaxLength(128)]
        public string assignee { get; set; }

        /// <summary>
        /// auto-generated id of the award.
        /// </summary>
        /// <example>d1e40c38-cc2a-445f-9eab-60c253256c57</example>
        [Guid]
        [Required]
        public string awardId { get; set; }

        /// <summary>
        /// description of the assignment
        /// </summary>
        /// <example>Apple Watch, 3 teams</example>
        [MaxLength(256)]
        public string description { get; set; }

        /// <summary>
        /// The timestamp when the assignment submitted.
        /// </summary>
        /// <example>2008-01-14T04:33:35Z</example>
        public DateTime createdAt { get; internal set; }

        /// <summary>
        /// The timestamp when the assignment updated.
        /// </summary>
        /// <example>2008-01-14T04:33:35Z</example>
        public DateTime updatedAt { get; internal set; }
    }
}
