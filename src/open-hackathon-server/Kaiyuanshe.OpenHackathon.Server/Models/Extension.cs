using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Models
{
    /// <summary>
    /// Extra properties, typically name-value pairs.
    /// </summary>
    public class Extension
    {
        /// <summary>
        /// name of the extension.
        /// </summary>
        [Required]
        [MaxLength(128)]
        public string name { get; set; }

        /// <summary>
        /// value of the extension
        /// </summary>
        [Required]
        [MaxLength(1024)]
        public string value { get; set; }
    }
}
