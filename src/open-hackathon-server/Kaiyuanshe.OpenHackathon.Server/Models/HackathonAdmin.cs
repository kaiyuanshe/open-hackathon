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

    public class HackathonAdminList : IResourceList<HackathonAdmin>
    {
        /// <summary>
        /// a list of admins
        /// </summary>
        public HackathonAdmin[] value { get; set; }

        /// <summary>
        ///  The URL the client should use to fetch the next page (per server side paging).
        ///  No more results if it's null or empty.
        /// </summary>
        public string nextLink { get; set; }
    }
}
