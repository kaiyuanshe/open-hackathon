using Kaiyuanshe.OpenHackathon.Server.Auth;
using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.AspNetCore.Authorization;
using Moq;
using NUnit.Framework;
using System.Collections.Generic;
using System.Security.Claims;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Auth
{
    public class TeamMemberHandlerTests
    {
        [Test]
        public async Task HandleAsyncTest_IsPlatformAdmin()
        {
            // data
            var requirements = new List<IAuthorizationRequirement>
            {
                new TeamAdministratorRequirement(),
            };
            var claims = new List<Claim>
            {
                ClaimsHelper.PlatformAdministrator("userid"),
            };
            var claimsPrincipal = new ClaimsPrincipal(new ClaimsIdentity(claims));
            TeamEntity teamEntity = new TeamEntity { };
            var hackathonAdminManagement = new Mock<IHackathonAdminManagement>();
            var teamManagement = new Mock<ITeamManagement>();
            var context = new AuthorizationHandlerContext(requirements, claimsPrincipal, teamEntity);

            // test
            var handler = new TeamAdministratorHandler(hackathonAdminManagement.Object, teamManagement.Object);
            await handler.HandleAsync(context);

            Assert.IsTrue(context.HasSucceeded);
            Mock.VerifyAll(hackathonAdminManagement, teamManagement);
            hackathonAdminManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
        }

        [Test]
        public async Task HandleAsyncTest_AnonymousUser()
        {
            // data
            var requirements = new List<IAuthorizationRequirement>
            {
                new TeamAdministratorRequirement(),
            };
            var claims = new List<Claim>
            {
            };
            var claimsPrincipal = new ClaimsPrincipal(new ClaimsIdentity(claims));
            TeamEntity teamEntity = new TeamEntity { };
            var hackathonManagement = new Mock<IHackathonAdminManagement>();
            var teamManagement = new Mock<ITeamManagement>();
            var context = new AuthorizationHandlerContext(requirements, claimsPrincipal, teamEntity);

            // test
            var handler = new TeamAdministratorHandler(hackathonManagement.Object, teamManagement.Object);
            await handler.HandleAsync(context);

            Assert.IsFalse(context.HasSucceeded);
            Mock.VerifyAll(hackathonManagement, teamManagement);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
        }

        [Test]
        public async Task HandleAsyncTest_IsHackathonAdmin()
        {
            // data
            string userid = "uid";
            var requirements = new List<IAuthorizationRequirement>
            {
                new TeamAdministratorRequirement(),
            };
            var claims = new List<Claim>
            {
                ClaimsHelper.UserId(userid),
            };
            var admins = new List<HackathonAdminEntity>
            {
                new HackathonAdminEntity{ RowKey = userid },
                new HackathonAdminEntity{ RowKey = "anotherId" },
            };
            var claimsPrincipal = new ClaimsPrincipal(new ClaimsIdentity(claims));
            TeamEntity teamEntity = new TeamEntity { PartitionKey = "hack" };
            var hackathonAdminManagement = new Mock<IHackathonAdminManagement>();
            hackathonAdminManagement.Setup(h => h.ListHackathonAdminAsync("hack", CancellationToken.None))
                .ReturnsAsync(admins);
            var teamManagement = new Mock<ITeamManagement>();
            var context = new AuthorizationHandlerContext(requirements, claimsPrincipal, teamEntity);

            // test
            var handler = new TeamAdministratorHandler(hackathonAdminManagement.Object, teamManagement.Object);
            await handler.HandleAsync(context);

            Assert.IsTrue(context.HasSucceeded);
            Mock.VerifyAll(hackathonAdminManagement, teamManagement);
            hackathonAdminManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
        }

        [Test]
        public async Task HandleAsyncTest_IsTeamAdmin()
        {
            // data
            string userid = "uid";
            var requirements = new List<IAuthorizationRequirement>
            {
                new TeamAdministratorRequirement()
            };
            var claims = new List<Claim>
            {
                ClaimsHelper.UserId(userid),
            };
            var admins = new List<HackathonAdminEntity>
            {
                new HackathonAdminEntity{ RowKey = "anotherId" },
            };
            var teamMembers = new List<TeamMemberEntity>
            {
                new TeamMemberEntity
                {
                    RowKey = userid,
                    Role = Server.Models.TeamMemberRole.Admin,
                    Status = Server.Models.TeamMemberStatus.approved,
                }
            };
            var claimsPrincipal = new ClaimsPrincipal(new ClaimsIdentity(claims));
            TeamEntity teamEntity = new TeamEntity { PartitionKey = "hack", RowKey = "tid" };
            var hackathonAdminManagement = new Mock<IHackathonAdminManagement>();
            hackathonAdminManagement.Setup(h => h.ListHackathonAdminAsync("hack", CancellationToken.None))
                .ReturnsAsync(admins);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.ListTeamMembersAsync("hack", "tid", CancellationToken.None))
                .ReturnsAsync(teamMembers);
            var context = new AuthorizationHandlerContext(requirements, claimsPrincipal, teamEntity);

            // test
            var handler = new TeamAdministratorHandler(hackathonAdminManagement.Object, teamManagement.Object);
            await handler.HandleAsync(context);

            Assert.IsTrue(context.HasSucceeded);
            Mock.VerifyAll(hackathonAdminManagement, teamManagement);
            hackathonAdminManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
        }

        [Test]
        public async Task HandleAsyncTest_IsNotTeamAdmin()
        {
            // data
            string userid = "uid";
            var requirements = new List<IAuthorizationRequirement>
            {
                new TeamAdministratorRequirement(),
            };
            var claims = new List<Claim>
            {
                ClaimsHelper.UserId(userid),
            };
            var admins = new List<HackathonAdminEntity>
            {
                new HackathonAdminEntity{ RowKey = "anotherId" },
            };
            var teamMembers = new List<TeamMemberEntity>
            {
                // not approved
                new TeamMemberEntity
                {
                    RowKey = userid,
                    Role = Server.Models.TeamMemberRole.Admin,
                    Status = Server.Models.TeamMemberStatus.pendingApproval,
                },
                // not Admin
                new TeamMemberEntity
                {
                    RowKey = userid,
                    Role = Server.Models.TeamMemberRole.Member,
                    Status = Server.Models.TeamMemberStatus.approved,
                },
                // id not match
                new TeamMemberEntity
                {
                    RowKey = "anotherid",
                    Role = Server.Models.TeamMemberRole.Admin,
                    Status = Server.Models.TeamMemberStatus.approved,
                },
            };
            var claimsPrincipal = new ClaimsPrincipal(new ClaimsIdentity(claims));
            TeamEntity teamEntity = new TeamEntity { PartitionKey = "hack", RowKey = "tid" };
            var hackathonAdminManagement = new Mock<IHackathonAdminManagement>();
            hackathonAdminManagement.Setup(h => h.ListHackathonAdminAsync("hack", CancellationToken.None))
                .ReturnsAsync(admins);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.ListTeamMembersAsync("hack", "tid", CancellationToken.None))
                .ReturnsAsync(teamMembers);
            var context = new AuthorizationHandlerContext(requirements, claimsPrincipal, teamEntity);

            // test
            var handler = new TeamAdministratorHandler(hackathonAdminManagement.Object, teamManagement.Object);
            await handler.HandleAsync(context);

            Assert.IsFalse(context.HasSucceeded);
            Mock.VerifyAll(hackathonAdminManagement, teamManagement);
            hackathonAdminManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
        }

        [Test]
        public async Task HandleAsyncTest_TeamMember()
        {
            // data
            string userid = "uid";
            var requirements = new List<IAuthorizationRequirement>
            {
                new TeamMemberRequirement()
            };
            var claims = new List<Claim>
            {
                ClaimsHelper.UserId(userid),
            };
            var admins = new List<HackathonAdminEntity>
            {
                new HackathonAdminEntity{ RowKey = "anotherId" },
            };
            var teamMembers = new List<TeamMemberEntity>
            {
                // not approved
                new TeamMemberEntity
                {
                    RowKey = userid,
                    Role = Server.Models.TeamMemberRole.Admin,
                    Status = Server.Models.TeamMemberStatus.pendingApproval,
                },
                // not Admin
                new TeamMemberEntity
                {
                    RowKey = userid,
                    Role = Server.Models.TeamMemberRole.Member,
                    Status = Server.Models.TeamMemberStatus.approved,
                },
                // id not match
                new TeamMemberEntity
                {
                    RowKey = "anotherid",
                    Role = Server.Models.TeamMemberRole.Admin,
                    Status = Server.Models.TeamMemberStatus.approved,
                },
            };
            var claimsPrincipal = new ClaimsPrincipal(new ClaimsIdentity(claims));
            TeamEntity teamEntity = new TeamEntity { PartitionKey = "hack", RowKey = "tid" };
            var hackathonAdminManagement = new Mock<IHackathonAdminManagement>();
            hackathonAdminManagement.Setup(h => h.ListHackathonAdminAsync("hack", CancellationToken.None))
                .ReturnsAsync(admins);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.ListTeamMembersAsync("hack", "tid", default))
                .ReturnsAsync(teamMembers);
            var context = new AuthorizationHandlerContext(requirements, claimsPrincipal, teamEntity);

            // test
            var handler = new TeamMemberHandler(hackathonAdminManagement.Object, teamManagement.Object);
            await handler.HandleAsync(context);

            Assert.IsTrue(context.HasSucceeded);
            Mock.VerifyAll(hackathonAdminManagement, teamManagement);
            hackathonAdminManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
        }
    }
}
