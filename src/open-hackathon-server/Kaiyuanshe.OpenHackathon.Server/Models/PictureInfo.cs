using Kaiyuanshe.OpenHackathon.Server.Models.Validations;
using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Models
{
    /// <summary>
    /// a class indicates a picture
    /// </summary>
    public class PictureInfo
    {
        /// <summary>
        /// name of the picture.
        /// </summary>
        /// <example>vehicle 1</example>
        [MaxLength(128)]
        public string name { get; set; }

        /// <summary>
        /// rich-text description of the picture. Can be used as alt text.
        /// </summary>
        /// <example>the rear view of the vehicle</example>
        [MaxLength(512)]
        public string description { get; set; }

        /// <summary>
        /// Uri of the picture. 
        /// If the picture is from a third-party website, please make sure it's allowed to be referenced by https://hackathon.kaiyuanshe.cn.
        /// </summary>
        /// <example>https://example.com/a.png</example>
        [Required]
        [MaxLength(256)]
        [AbsoluteUri]
        public string uri { get; set; }
    }
}
