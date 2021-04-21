using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.AspNetCore.Authorization;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Auth
{
    public class TeamAdministratorRequirement : IAuthorizationRequirement
    {
    }

    public class TeamAdministratorHandler : AuthorizationHandler<TeamAdministratorRequirement, TeamEntity>
    {
        protected override Task HandleRequirementAsync(AuthorizationHandlerContext context, TeamAdministratorRequirement requirement, TeamEntity resource)
        {
            throw new NotImplementedException();
        }
    }
}
