using System.ComponentModel.DataAnnotations;

namespace Kaiyuanshe.OpenHackathon.Server.Models
{
    /// <summary>
    /// Represents a person who can review and rate the works
    /// </summary>
    public class Judge : ModelBase
    {
        /// <summary>
        /// name of hackathon
        /// </summary>
        /// <example>foo</example>
        public string hackathonName { get; internal set; }

        /// <summary>
        /// id of judge
        /// </summary>
        /// <example>1</example>
        public string userId { get; internal set; }

        /// <summary>
        /// user info of the judge.
        /// </summary>
        public UserInfo user { get; internal set; }

        /// <summary>
        /// description of the Judge
        /// </summary>
        /// <example>Professor of Computer Science, Tsinghua University</example>
        [MaxLength(256)]
        public string description { get; set; }
    }

    public class JudgeList : ResourceList<Judge>
    {
        /// <summary>
        /// a list of judges
        /// </summary>
        public override Judge[] value { get; set; }
    }
}
