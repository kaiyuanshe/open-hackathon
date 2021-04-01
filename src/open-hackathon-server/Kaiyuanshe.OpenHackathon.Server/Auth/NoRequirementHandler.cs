using Microsoft.AspNetCore.Authorization;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Auth
{
    public class NoRequirement : IAuthorizationRequirement
    {
    }

    public class NoRequirementHandler : AuthorizationHandler<NoRequirement>
    {
        protected override Task HandleRequirementAsync(AuthorizationHandlerContext context, NoRequirement requirement)
        {
            if ((context.User?.Identity?.IsAuthenticated).GetValueOrDefault(false))
            {
                context.Succeed(requirement);
            }

            return Task.CompletedTask;
        }
    }
}
