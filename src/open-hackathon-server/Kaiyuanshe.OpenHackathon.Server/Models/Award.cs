using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Models
{
    public class Award
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
        public string name { get; set; }

        /// <summary>
        /// description of the award
        /// </summary>
        /// <example>Apple Watch, 3 teams</example>
        public string description { get; set; }

        /// <summary>
        /// quantity of the award.
        /// </summary>
        /// <example>3</example>
        public int quantity { get; set; }

        /// <summary>
        /// target whom the award is given. team or individual.
        /// </summary>
        /// <example>team</example>
        public AwardTarget target { get; set; }

        /// <summary>
        /// A list of images of the award. To add a new picture, be sure to submit all pictures in request including the existing ones. 
        /// The entire list will be replaced with list in request.
        /// </summary>
        public PictureInfo[] pictures { get; set; }

        /// <summary>
        /// The timestamp when the award submitted.
        /// </summary>
        /// <example>2008-01-14T04:33:35Z</example>
        public DateTime createdAt { get; internal set; }

        /// <summary>
        /// The timestamp when the award updated.
        /// </summary>
        /// <example>2008-01-14T04:33:35Z</example>
        public DateTime updatedAt { get; internal set; }
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
