using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Models
{
    /// <summary>
    /// represents an award which can be assigned to a team or an individual.
    /// </summary>
    public class Award: ModelBase
    {
        /// <summary>
        /// name of hackathon
        /// </summary>
        /// <example>foo</example>
        public string hackathonName { get; internal set; }

        /// <summary>
        /// auto-generated id of the award.
        /// </summary>
        /// <example>d1e40c38-cc2a-445f-9eab-60c253256c57</example>
        public string id { get; internal set; }

        /// <summary>
        /// Name of the award.
        /// </summary>
        /// <example>一等奖</example>
        [MaxLength(64)]
        public string name { get; set; }

        /// <summary>
        /// description of the award
        /// </summary>
        /// <example>Apple Watch, 3 teams</example>
        [MaxLength(256)]
        public string description { get; set; }

        /// <summary>
        /// quantity of the award. 1 by default.
        /// </summary>
        /// <example>3</example>
        [Range(1, 10_000)]
        public int? quantity { get; set; }

        /// <summary>
        /// target whom the award is given. team or individual. team by default.
        /// </summary>
        /// <example>team</example>
        public AwardTarget? target { get; set; }

        /// <summary>
        /// A list of images of the award. To add a new picture, be sure to submit all pictures in request including the existing ones. 
        /// The entire list will be replaced with list in request.
        /// </summary>
        [MaxLength(50)]
        public PictureInfo[] pictures { get; set; }
    }

    /// <summary>
    /// target to award
    /// </summary>
    public enum AwardTarget
    {
        team,
        individual,
    }

    /// <summary>
    /// a list of enrollment
    /// </summary>
    public class AwardList : IResourceList<Award>
    {
        /// <summary>
        /// a list of Award
        /// </summary>
        public Award[] value { get; set; }

        /// <summary>
        ///  The URL the client should use to fetch the next page (per server side paging).
        ///  No more results if it's null or empty.
        /// </summary>
        public string nextLink { get; set; }
    }
}
