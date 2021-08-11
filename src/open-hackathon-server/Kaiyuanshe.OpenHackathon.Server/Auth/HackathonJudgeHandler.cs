using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.AspNetCore.Authorization;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Auth
{
    public class HackathonJudgeRequirement : IAuthorizationRequirement
    {

    }

    public class HackathonJudgeHandler : AuthorizationHandler<HackathonJudgeRequirement, HackathonEntity>
    {
        IHackathonAdminManagement HackathonAdminManagement { get; set; }
        IJudgeManagement JudgeManagement { get; set; }

        public HackathonJudgeHandler(IHackathonAdminManagement hackathonAdminManagement, IJudgeManagement judgeManagement)
        {
            HackathonAdminManagement = hackathonAdminManagement;
            JudgeManagement = judgeManagement;
        }

        protected override async Task HandleRequirementAsync(AuthorizationHandlerContext context, HackathonJudgeRequirement requirement, HackathonEntity resource)
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

            // hackathon admin
            var hackathonAdmins = await HackathonAdminManagement.ListHackathonAdminAsync(resource.Name);
            if (hackathonAdmins.Any(a => a.UserId == userId))
            {
                context.Succeed(requirement);
                return;
            }

            // hackathon judge
            if (await JudgeManagement.IsJudgeAsync(resource.Name, userId))
            {
                context.Succeed(requirement);
            }
        }
    }
}
