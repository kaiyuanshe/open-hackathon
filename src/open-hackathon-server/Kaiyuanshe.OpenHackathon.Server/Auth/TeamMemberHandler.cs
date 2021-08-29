using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.AspNetCore.Authorization;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Auth
{
    public class TeamAdministratorRequirement : IAuthorizationRequirement
    {
    }

    public class TeamMemberRequirement : IAuthorizationRequirement
    {
    }

    public abstract class TeamMemberBaseHandler<TRequirement> : AuthorizationHandler<TRequirement, TeamEntity>
        where TRequirement : IAuthorizationRequirement
    {
        IHackathonAdminManagement HackathonAdminManagement { get; set; }
        ITeamManagement TeamManagement { get; set; }

        protected abstract Task HandleTeamRequirementAsync(AuthorizationHandlerContext context, TRequirement requirement, TeamEntity resource, TeamMemberEntity teamMember);

        public TeamMemberBaseHandler(IHackathonAdminManagement hackathonAdminManagement, ITeamManagement teamManagement)
        {
            HackathonAdminManagement = hackathonAdminManagement;
            TeamManagement = teamManagement;
        }

        protected override async Task HandleRequirementAsync(AuthorizationHandlerContext context, TRequirement requirement, TeamEntity resource)
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

            var hackathonAdmins = await HackathonAdminManagement.ListHackathonAdminAsync(resource.HackathonName);
            if (hackathonAdmins.Any(a => a.UserId == userId))
            {
                context.Succeed(requirement);
                return;
            }
            
            // creator
            if( resource.CreatorId == userId)
            {
                context.Succeed(requirement);
                return;
            }

            var teamMembers = await TeamManagement.ListTeamMembersAsync(resource.HackathonName, resource.Id);
            var teamMember = teamMembers.FirstOrDefault(m => m.UserId == userId && m.Status == Models.TeamMemberStatus.approved);
            if (teamMember != null)
            {
                await HandleTeamRequirementAsync(context, requirement, resource, teamMember);
            }
        }
    }

    public class TeamAdministratorHandler : TeamMemberBaseHandler<TeamAdministratorRequirement>
    {
        public TeamAdministratorHandler(IHackathonAdminManagement hackathonAdminManagement, ITeamManagement teamManagement)
            : base(hackathonAdminManagement, teamManagement)
        {
        }

        protected override Task HandleTeamRequirementAsync(AuthorizationHandlerContext context, TeamAdministratorRequirement requirement, TeamEntity resource, TeamMemberEntity teamMember)
        {
            if (teamMember.Role == Models.TeamMemberRole.Admin)
            {
                context.Succeed(requirement);
            }

            return Task.CompletedTask;
        }
    }

    public class TeamMemberHandler : TeamMemberBaseHandler<TeamMemberRequirement>
    {
        public TeamMemberHandler(IHackathonAdminManagement hackathonAdminManagement, ITeamManagement teamManagement)
            : base(hackathonAdminManagement, teamManagement)
        {
        }

        protected override Task HandleTeamRequirementAsync(AuthorizationHandlerContext context, TeamMemberRequirement requirement, TeamEntity resource, TeamMemberEntity teamMember)
        {
            context.Succeed(requirement);
            return Task.CompletedTask;
        }
    }
}
