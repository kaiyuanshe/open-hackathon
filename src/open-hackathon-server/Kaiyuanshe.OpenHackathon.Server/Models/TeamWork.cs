using Kaiyuanshe.OpenHackathon.Server.Models.Validations;
using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Models
{
    /// <summary>
    /// Describes a work published by a team. A work might be an image, an Url of demo website, a video, a Microsoft Word doc, a PowerPoint doc etc.
    /// </summary>
    public class TeamWork : ModelBase
    {
        /// <summary>
        /// Id of the team
        /// </summary>
        /// <example>d1e40c38-cc2a-445f-9eab-60c253256c57</example>
        public string teamId { get; internal set; }

        /// <summary>
        /// auto-generated id of the work.
        /// </summary>
        /// <example>c85e65ef-fd5e-4539-a1f8-bafb7e4f9d74</example>
        public string id { get; internal set; }

        /// <summary>
        /// name of hackathon
        /// </summary>
        /// <example>foo</example>
        public string hackathonName { get; internal set; }

        /// <summary>
        /// title of the work. Requried for creation.
        /// </summary>
        /// <example>the homepage</example>
        [MaxLength(64)]
        public string title { get; set; }

        /// <summary>
        /// description of the work
        /// </summary>
        /// <example>the homepage</example>
        [MaxLength(512)]
        public string description { get; set; }

        /// <summary>
        /// type of the work. Default to website.
        /// </summary>
        /// <example>image</example>
        public TeamWorkType? type { get; set; }

        /// <summary>
        /// Uri of the work. Requried for creation.
        /// If the url is from a third-party website, please make sure it's allowed to be referenced by https://hackathon.kaiyuanshe.cn.
        /// </summary>
        /// <example>https://hackathon-api.static.kaiyuanshe.cn/user/2020/01/01/avatar.png</example>
        [MaxLength(256)]
        [AbsoluteUri]
        public string url { get; set; }
    }

    /// <summary>
    /// Type of the work
    /// </summary>
    public enum TeamWorkType
    {
        /// <summary>
        /// An image: jpg, png, gif etc.
        /// </summary>
        image,
        /// <summary>
        /// A website demonstrating your work.
        /// </summary>
        website,
        /// <summary>
        /// A video like youtube.
        /// </summary>
        video,
        /// <summary>
        /// A Microsoft Word doc
        /// </summary>
        word,
        /// <summary>
        /// A Microsoft PowerPoint doc
        /// </summary>
        powerpoint
    }

    /// <summary>
    /// a list of team works
    /// </summary>
    public class TeamWorkList : ResourceList<TeamWork>
    {
        /// <summary>
        /// a list of team works
        /// </summary>
        public override TeamWork[] value { get; set; }
    }
}
