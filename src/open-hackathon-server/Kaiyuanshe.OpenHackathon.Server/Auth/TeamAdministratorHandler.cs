using Kaiyuanshe.OpenHackathon.Server.Biz;
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
        IHackathonManagement HackathonManagement { get; set; }
        ITeamManagement TeamManagement { get; set; }

        public TeamAdministratorHandler(IHackathonManagement hackathonManagement, ITeamManagement teamManagement)
        {
            HackathonManagement = hackathonManagement;
            TeamManagement = teamManagement;
        }

        protected override async Task HandleRequirementAsync(AuthorizationHandlerContext context, TeamAdministratorRequirement requirement, TeamEntity resource)
        {
            if (ClaimsHelper.IsPlatformAdministrator(context.User))
            {
                context.Succeed(requirement);
                return;
            }

            string userId = context?.User?.Claims?.FirstOrDefault(c => c.Type == AuthConstant.ClaimType.UserId)?.Value;
            if (string.IsNullOrEmpty(userId))
            {
                // anonymous user
                return;
            }

            var hackathonAdmins = await HackathonManagement.ListHackathonAdminAsync(resource.HackathonName);
            if (hackathonAdmins.Any(a => a.UserId == userId))
            {
                context.Succeed(requirement);
                return;
            }

            var teamMembers = await TeamManagement.ListTeamMembersAsync(resource.Id);
            if (teamMembers.Any(m => m.UserId == userId && m.Role == Models.TeamMemberRole.Admin && m.Status == Models.TeamMemberStatus.approved))
            {
                context.Succeed(requirement);
            }
        }
    }
}
