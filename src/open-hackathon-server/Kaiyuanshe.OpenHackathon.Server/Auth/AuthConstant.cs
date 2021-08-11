using System.Security.Claims;

namespace Kaiyuanshe.OpenHackathon.Server.Auth
{
    /// <summary>
    /// Constants related to <seealso cref="Claim"/>
    /// </summary>
    public static class AuthConstant
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
        }

        public static class Policy
        {
            /// <summary>
            /// Policy to administrate a hackathon. See <seealso cref="HackathonAdministratorHandler"/> for details.
            /// </summary>
            public const string HackathonAdministrator = "HackathonAdministratorReal";

            /// <summary>
            /// Policy to rate a team and its works.
            /// </summary>
            public const string HackathonJudge = "HackathonJudgeReal";

            /// <summary>
            /// Administrator of the OPH platform.
            /// </summary>
            public const string PlatformAdministrator = "PlatformAdministrator";

            /// <summary>
            /// Administrator of a team.
            /// </summary>
            public const string TeamAdministrator = "TeamAdministratorReal";

            /// <summary>
            /// Member of a team.
            /// </summary>
            public const string TeamMember = "TeamMemberReal";
        }

        /// <summary>
        /// Only for swagger, which shows the policy name on Swagger UI but no requirement needs to meet.
        /// <seealso cref="Policy"/> is the one for real access check. Most of the policies are resource based,
        /// either hackathon-based or team-based, so Authorize(Policy="...") doesn't work.
        /// </summary>
        public static class PolicyForSwagger
        {
            /// <summary>
            /// Policy to administrate a hackathon.
            /// </summary>
            public const string HackathonAdministrator = "HackathonAdministrator";

            /// <summary>
            /// Policy to rate a team and its works.
            /// </summary>
            public const string HackathonJudge = "HackathonJudge";

            /// <summary>
            /// Policy to administrate a team.
            /// </summary>
            public const string TeamAdministrator = "TeamAdministrator";

            /// <summary>
            /// Policy for a team member.
            /// </summary>
            public const string TeamMember = "TeamMember";

            /// <summary>
            /// Policy to allow login user.
            /// </summary>
            public const string LoginUser = "LoginUser";
        }
    }
}
