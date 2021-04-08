using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Claims;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Auth
{
    public static class ClaimsHelper
    {
        public static Claim UserId(string userId)
        {
            return new Claim(
                    AuthConstant.ClaimType.UserId,
                    userId,
                    ClaimValueTypes.String,
                    AuthConstant.Issuer.Default);
        }

        public static Claim PlatformAdministrator(string userId)
        {
            return new Claim(
                    AuthConstant.ClaimType.PlatformAdministrator,
                    userId,
                    ClaimValueTypes.String,
                    AuthConstant.Issuer.Default);
        }

        public static bool IsPlatformAdministrator(ClaimsPrincipal claimsPrincipal)
        {
            if (claimsPrincipal == null)
                return false;

            return claimsPrincipal.HasClaim(c =>
            {
                return c.Type == AuthConstant.ClaimType.PlatformAdministrator;
            });
        }

        public static string GetUserId(ClaimsPrincipal claimsPrincipal)
        {
            var userIdClaim = claimsPrincipal?.Claims?.FirstOrDefault(c => c.Type == AuthConstant.ClaimType.UserId);
            return userIdClaim?.Value ?? string.Empty;
        }
    }
}
