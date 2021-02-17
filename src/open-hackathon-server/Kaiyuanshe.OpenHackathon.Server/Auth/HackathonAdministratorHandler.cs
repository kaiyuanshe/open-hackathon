using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.AspNetCore.Authorization;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Auth
{
    public class HackathonAdministratorRequirement : IAuthorizationRequirement
    {

    }

    public class HackathonAdministratorHandler : AuthorizationHandler<HackathonAdministratorRequirement, HackathonEntity>
    {
        protected override Task HandleRequirementAsync(AuthorizationHandlerContext context, HackathonAdministratorRequirement requirement, HackathonEntity resource)
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
