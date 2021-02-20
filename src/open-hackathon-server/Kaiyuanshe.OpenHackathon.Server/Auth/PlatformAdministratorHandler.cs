using Microsoft.AspNetCore.Authorization;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Auth
{
    public class PlatformAdministratorRequirement : IAuthorizationRequirement
    {

    }

    public class PlatformAdministratorHandler : AuthorizationHandler<PlatformAdministratorRequirement>
    {
        protected override Task HandleRequirementAsync(AuthorizationHandlerContext context, PlatformAdministratorRequirement requirement)
        {
            if (ClaimsHelper.IsPlatformAdministrator(context.User))
            {
                context.Succeed(requirement);
            }

            return Task.CompletedTask;
        }
    }
}
