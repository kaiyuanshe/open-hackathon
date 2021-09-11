using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Models
{
    /// <summary>
    /// Administrator of a hackathon
    /// </summary>
    public class HackathonAdmin : ModelBase
    {
        /// <summary>
        /// name of hackathon
        /// </summary>
        /// <example>foo</example>
        public string hackathonName { get; internal set; }

        /// <summary>
        /// user id of admin
        /// </summary>
        /// <example>1</example>
        public string userId { get; internal set; }

        /// <summary>
        /// detailed user info of the admin.
        /// </summary>
        public UserInfo user { get; internal set; }
    }

    public class HackathonAdminList : ResourceList<HackathonAdmin>
    {
        /// <summary>
        /// a list of admins
        /// </summary>
        public override HackathonAdmin[] value { get; set; }
    }
}
