using Kaiyuanshe.OpenHackathon.Server.Models.Validations;
using System;
using System.ComponentModel.DataAnnotations;

namespace Kaiyuanshe.OpenHackathon.Server.Models
{
    /// <summary>
    /// Represents ratings(scores) from the judges
    /// </summary>
    public class Rating : ModelBase
    {
        /// <summary>
        /// name of hackathon
        /// </summary>
        /// <example>foo</example>
        public string hackathonName { get; internal set; }

        /// <summary>
        /// Auto-generated Guid of the rating.
        /// </summary>
        /// <example>dd09af6d-75f6-463c-8e5d-786818e409db</example>
        public string id { get; internal set; }

        /// <summary>
        /// user id of judge.
        /// </summary>
        /// <example>1</example>
        public string judgeId { get; internal set; }

        /// <summary>
        /// user info of the judge.
        /// </summary>
        public UserInfo judge { get; internal set; }

        /// <summary>
        /// id of rating kind. Cannot be updated.
        /// </summary>
        /// <example>e4576366-fa87-451d-8e4d-ef6d1b6cee05</example>
        [RequiredIfPut]
        [Guid]
        public string ratingKindId { get; set; }

        /// <summary>
        /// detail of the rating kind
        /// </summary>
        public RatingKind ratingKind { get; internal set; }

        /// <summary>
        /// id of the team. Required for first time create(PUT) request. Cannot be updated.
        /// </summary>
        /// <example>d1e40c38-cc2a-445f-9eab-60c253256c57</example>
        [Guid]
        [RequiredIfPut]
        public string teamId { get; set; }

        /// <summary>
        /// team detail.
        /// </summary>
        public Team team { get; internal set; }

        /// <summary>
        /// rating(score). an integer between 0 and allowed maximum value. Required for first time create(PUT) request.
        /// </summary>
        /// <example>5</example>
        [Range(0, 10000)]
        [RequiredIfPut]
        public int? score { get; set; }

        /// <summary>
        /// description of the rating
        /// </summary>
        /// <example>amazing team</example>
        [MaxLength(256)]
        public string description { get; set; }
    }

    public class RatingList : ResourceList<Rating>
    {
        /// <summary>
        /// a list of ratings.
        /// </summary>
        public override Rating[] value { get; set; }
    }
}
