using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Claims;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Authorize
{
    /// <summary>
    /// Constants related to <seealso cref="Claim"/>
    /// </summary>
    public static class ClaimConstants
    {
        public static class Issuer
        {
            public const string Default = "Open Hackathon";
        }

        public static class AuthType
        {
            public const string Token = "token";
        }

        /// <summary>
        /// Type of <seealso cref="Claim"/>.
        /// </summary>
        public static class ClaimType
        {
            /// <summary>
            /// Type for user's Id. Claim value is user.Id
            /// </summary>
            public const string UserId = "UserId";

            /// <summary>
            /// type for PlatformAdministrator, whoever has this type of Claim is an Admin of Open Hackathon platform. 
            /// Claim value can be any string, typically the user's id.
            /// </summary>
            public const string PlatformAdministrator = "PlatformAdministrator";

            /// <summary>
            /// Administrator of a hackathon. The creator who creates the hackathon is an Admin by default.
            /// Claim value: hackathon Name.
            /// </summary>
            public const string HackathonAdministrator = "HackathonAdministrator";

            /// <summary>
            /// Judge of a hackathon.
            /// Claim value: hackathon Name.
            /// </summary>
            public const string HackathonJudge = "HackathonJudge";

            /// <summary>
            /// Contestant of a hackathon.
            /// Claim value: hackathon Name.
            /// </summary>
            public const string HackathonContestant = "HackathonContestant";

            /// <summary>
            /// Admin of a team. Who creates the team is Admin by default.
            /// Claim value: {hackathon Name}.{team Id}
            /// </summary>
            public const string TeamAdministrator = "TeamAdministrator";

            /// <summary>
            /// Member of a team. Everyone in a team is a TeamMember.
            /// Claim value: {hackathon Name}.{team Id}
            /// </summary>
            public const string TeamMember = "TeamMember";
        }

        public static class Policy
        {
            /// <summary>
            /// Policy to administrate a hackathon.
            /// 
            /// Allowed claims: PlatformAdministrator, HackathonAdministrator
            /// </summary>
            public const string HackathonAdministrator = "HackathonAdministrator";
        }
    }
}
