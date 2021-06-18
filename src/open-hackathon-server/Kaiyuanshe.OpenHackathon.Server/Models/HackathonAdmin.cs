using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Models
{
    /// <summary>
    /// Administrator of a hackathon
    /// </summary>
    public class HackathonAdmin
    {
        /// <summary>
        /// name of hackathon
        /// </summary>
        /// <example>foo</example>
        public string hackathonName { get; internal set; }

        /// <summary>
        /// id of user
        /// </summary>
        /// <example>1</example>
        public string userId { get; set; }

        /// <summary>
        /// The timestamp when the enrollment submitted.
        /// </summary>
        /// <example>2008-01-14T04:33:35Z</example>
        public DateTime createdAt { get; internal set; }

        /// <summary>
        /// The timestamp when the enrollment updated.
        /// </summary>
        /// <example>2008-01-14T04:33:35Z</example>
        public DateTime updatedAt { get; internal set; }
    }
}
