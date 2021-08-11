using Kaiyuanshe.OpenHackathon.Server.Auth;
using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.AspNetCore.Authorization;
using Moq;
using NUnit.Framework;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Claims;
using System.Text;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Auth
{
    public class HackathonJudgeHandlerTests
    {
        [Test]
        public async Task HandleAsyncTest_IsPlatformAdmin()
        {
            // data
            var requirements = new List<IAuthorizationRequirement>
            {
                new HackathonJudgeRequirement(),
            };
            var claims = new List<Claim>
            {
                ClaimsHelper.PlatformAdministrator("userid"),
            };
            var claimsPrincipal = new ClaimsPrincipal(new ClaimsIdentity(claims));
            HackathonEntity hackathonEntity = new HackathonEntity { };
            var hackathonAdminManagement = new Mock<IHackathonAdminManagement>();
            var judgeManagement = new Mock<IJudgeManagement>();
            var context = new AuthorizationHandlerContext(requirements, claimsPrincipal, hackathonEntity);

            // test
            var handler = new HackathonJudgeHandler(hackathonAdminManagement.Object, judgeManagement.Object);
            await handler.HandleAsync(context);

            Assert.IsTrue(context.HasSucceeded);
            Mock.VerifyAll(hackathonAdminManagement, judgeManagement);
            hackathonAdminManagement.VerifyNoOtherCalls();
            judgeManagement.VerifyNoOtherCalls();
        }

        [Test]
        public async Task HandleAsyncTest_AnonymousUser()
        {
            // data
            var requirements = new List<IAuthorizationRequirement>
            {
                new HackathonJudgeRequirement(),
            };
            var claims = new List<Claim>
            {
            };
            var claimsPrincipal = new ClaimsPrincipal(new ClaimsIdentity(claims));
            HackathonEntity hackathonEntity = new HackathonEntity { };
            var hackathonAdminManagement = new Mock<IHackathonAdminManagement>();
            var judgeManagement = new Mock<IJudgeManagement>();
            var context = new AuthorizationHandlerContext(requirements, claimsPrincipal, hackathonEntity);

            // test
            var handler = new HackathonJudgeHandler(hackathonAdminManagement.Object, judgeManagement.Object);
            await handler.HandleAsync(context);

            Assert.IsFalse(context.HasSucceeded);
            Mock.VerifyAll(hackathonAdminManagement, judgeManagement);
            hackathonAdminManagement.VerifyNoOtherCalls();
            judgeManagement.VerifyNoOtherCalls();
        }

        [Test]
        public async Task HandleAsyncTest_IsHackathonAdmin()
        {
            // data
            var requirements = new List<IAuthorizationRequirement>
            {
                new HackathonJudgeRequirement(),
            };
            var claims = new List<Claim>
            {
                ClaimsHelper.UserId("userid"),
            };
            var admins = new List<HackathonAdminEntity>
            {
                new HackathonAdminEntity{ RowKey = "userid" },
                new HackathonAdminEntity{ RowKey = "anotherId" },
            };
            var claimsPrincipal = new ClaimsPrincipal(new ClaimsIdentity(claims));
            HackathonEntity hackathonEntity = new HackathonEntity { PartitionKey = "hack" };

            var hackathonAdminManagement = new Mock<IHackathonAdminManagement>();
            hackathonAdminManagement.Setup(h => h.ListHackathonAdminAsync("hack", default)).ReturnsAsync(admins);
            var judgeManagement = new Mock<IJudgeManagement>();
            var context = new AuthorizationHandlerContext(requirements, claimsPrincipal, hackathonEntity);

            // test
            var handler = new HackathonJudgeHandler(hackathonAdminManagement.Object, judgeManagement.Object);
            await handler.HandleAsync(context);

            Assert.IsTrue(context.HasSucceeded);
            Mock.VerifyAll(hackathonAdminManagement, judgeManagement);
            hackathonAdminManagement.VerifyNoOtherCalls();
            judgeManagement.VerifyNoOtherCalls();
        }

        [TestCase(true)]
        [TestCase(false)]
        public async Task HandleAsyncTest_IsHackathonJudge(bool isJudge)
        {
            // data
            var requirements = new List<IAuthorizationRequirement>
            {
                new HackathonJudgeRequirement(),
            };
            var claims = new List<Claim>
            {
                ClaimsHelper.UserId("userid"),
            };
            var admins = new List<HackathonAdminEntity>
            {
                new HackathonAdminEntity{ RowKey = "anotherId" },
            };
            var claimsPrincipal = new ClaimsPrincipal(new ClaimsIdentity(claims));
            HackathonEntity hackathonEntity = new HackathonEntity { PartitionKey = "hack" };

            var hackathonAdminManagement = new Mock<IHackathonAdminManagement>();
            hackathonAdminManagement.Setup(h => h.ListHackathonAdminAsync("hack", default)).ReturnsAsync(admins);
            var judgeManagement = new Mock<IJudgeManagement>();
            judgeManagement.Setup(j => j.IsJudgeAsync("hack", "userid", default)).ReturnsAsync(isJudge);
            var context = new AuthorizationHandlerContext(requirements, claimsPrincipal, hackathonEntity);

            // test
            var handler = new HackathonJudgeHandler(hackathonAdminManagement.Object, judgeManagement.Object);
            await handler.HandleAsync(context);

            Assert.AreEqual(isJudge, context.HasSucceeded);
            Mock.VerifyAll(hackathonAdminManagement, judgeManagement);
            hackathonAdminManagement.VerifyNoOtherCalls();
            judgeManagement.VerifyNoOtherCalls();
        }
    }
}
