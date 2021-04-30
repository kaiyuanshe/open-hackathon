using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.AspNetCore.Authorization;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Auth
{
    public class TeamMemberRequirement : IAuthorizationRequirement
    {
        public bool AdminRequired { get; set; }
    }

    public class TeamMemberHandler : AuthorizationHandler<TeamMemberRequirement, TeamEntity>
    {
        IHackathonManagement HackathonManagement { get; set; }
        ITeamManagement TeamManagement { get; set; }

        public TeamMemberHandler(IHackathonManagement hackathonManagement, ITeamManagement teamManagement)
        {
            HackathonManagement = hackathonManagement;
            TeamManagement = teamManagement;
        }

        protected override async Task HandleRequirementAsync(AuthorizationHandlerContext context, TeamMemberRequirement requirement, TeamEntity resource)
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
            var teamMember = teamMembers.FirstOrDefault(m => m.UserId == userId && m.Status == Models.TeamMemberStatus.approved);
            if (teamMember != null)
            {
                if (requirement.AdminRequired && teamMember.Role == Models.TeamMemberRole.Admin)
                {
                    context.Succeed(requirement);
                }
                else if (!requirement.AdminRequired)
                {
                    context.Succeed(requirement);
                }
            }
        }
    }
}
