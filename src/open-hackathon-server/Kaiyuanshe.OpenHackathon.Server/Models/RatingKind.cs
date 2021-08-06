using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Models
{
    /// <summary>
    /// Describes a kind of rating. Hackathon admins can define multiple kinds so judges can give ratings on each kind.
    /// </summary>
    public class RatingKind : ModelBase
    {
        /// <summary>
        /// name of hackathon
        /// </summary>
        /// <example>foo</example>
        public string hackathonName { get; internal set; }

        /// <summary>
        /// auto-generated id of the kind.
        /// </summary>
        /// <example>d1e40c38-cc2a-445f-9eab-60c253256c57</example>
        public string id { get; internal set; }

        /// <summary>
        /// Name of the kind.
        /// </summary>
        /// <example>创意性</example>
        [MaxLength(64)]
        public string name { get; set; }

        /// <summary>
        /// description of the kind
        /// </summary>
        /// <example>the level of creativity.</example>
        [MaxLength(256)]
        public string description { get; set; }

        /// <summary>
        /// maximum rating accepted. default to 10. Ratings given by judges must be between 0 and this maximum value.
        /// </summary>
        /// <example>0</example>
        [Range(1, 10_000)]
        public int? maximumRating { get; set; }
    }

    /// <summary>
    /// a list of enrollment
    /// </summary>
    public class RatingKindList : IResourceList<RatingKind>
    {
        /// <summary>
        /// a list of RatingKinds
        /// </summary>
        public RatingKind[] value { get; set; }

        /// <summary>
        ///  The URL the client should use to fetch the next page (per server side paging).
        ///  No more results if it's null or empty.
        /// </summary>
        public string nextLink { get; set; }
    }
}
