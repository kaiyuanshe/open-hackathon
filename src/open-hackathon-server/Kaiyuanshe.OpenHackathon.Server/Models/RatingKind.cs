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
        /// <example>e4576366-fa87-451d-8e4d-ef6d1b6cee05</example>
        public string id { get; internal set; }

        /// <summary>
        /// Name of the kind.
        /// </summary>
        /// <example>创意性</example>
        [MaxLength(64)]
        [Required]
        public string name { get; set; }

        /// <summary>
        /// description of the kind
        /// </summary>
        /// <example>the level of creativity.</example>
        [MaxLength(256)]
        public string description { get; set; }

        /// <summary>
        /// maximum score accepted. default to 10. Ratings given by judges must be between 0 and this maximum value.
        /// </summary>
        /// <example>10</example>
        [Range(1, 10_000)]
        public int? maximumScore { get; set; }
    }

    /// <summary>
    /// a list of enrollment
    /// </summary>
    public class RatingKindList : ResourceList<RatingKind>
    {
        /// <summary>
        /// a list of RatingKinds
        /// </summary>
        public override RatingKind[] value { get; set; }
    }
}
