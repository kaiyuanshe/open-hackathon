using Microsoft.AspNetCore.Authorization;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Authorize
{
    public class HackathonAdministratorRequirement : IAuthorizationRequirement
    {

    }

    public class HackathonAdministratorHandler : AuthorizationHandler<HackathonAdministratorRequirement>
    {
        protected override Task HandleRequirementAsync(AuthorizationHandlerContext context, HackathonAdministratorRequirement requirement)
        {
            if (ClaimsHelper.IsPlatformAdministrator(context.User))
            {
                context.Succeed(requirement);
            }

            // TODO HackahontAdministrator

            return Task.CompletedTask;
        }
    }
}
