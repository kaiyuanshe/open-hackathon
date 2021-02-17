using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Claims;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Authorize
{
    public static class ClaimsHelper
    {
        public static Claim UserId(string userId)
        {
            return new Claim(
                    ClaimConstants.ClaimType.UserId,
                    userId,
                    ClaimValueTypes.String,
                    ClaimConstants.Issuer.Default);
        }

        public static Claim PlatformAdministrator(string userId)
        {
            return new Claim(
                    ClaimConstants.ClaimType.PlatformAdministrator,
                    userId,
                    ClaimValueTypes.String,
                    ClaimConstants.Issuer.Default);
        }

        public static bool IsPlatformAdministrator(ClaimsPrincipal claimsPrincipal)
        {
            if (claimsPrincipal == null)
                return false;

            return claimsPrincipal.HasClaim(c =>
            {
                return c.Type == ClaimConstants.ClaimType.PlatformAdministrator;
            });
        }
    }
}
