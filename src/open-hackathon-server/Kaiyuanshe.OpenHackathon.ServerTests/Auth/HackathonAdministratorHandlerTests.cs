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
    [TestFixture]
    public class HackathonAdministratorHandlerTests
    {
        [Test]
        public async Task HandleAsyncTest_IsPlatformAdmin()
        {
            // data
            var requirements = new List<IAuthorizationRequirement>
            {
                new HackathonAdministratorRequirement(),
            };
            var claims = new List<Claim>
            {
                ClaimsHelper.PlatformAdministrator("userid"),
            };
            var claimsPrincipal = new ClaimsPrincipal(new ClaimsIdentity(claims));
            HackathonEntity hackathonEntity = new HackathonEntity { };
            var hackathonAdminManagement = new Mock<IHackathonAdminManagement>();
            var context = new AuthorizationHandlerContext(requirements, claimsPrincipal, hackathonEntity);

            // test
            var handler = new HackathonAdministratorHandler(hackathonAdminManagement.Object);
            await handler.HandleAsync(context);

            Assert.IsTrue(context.HasSucceeded);
            Mock.VerifyAll(hackathonAdminManagement);
            hackathonAdminManagement.VerifyNoOtherCalls();
        }

        [Test]
        public async Task HandleAsyncTest_AnonymousUser()
        {
            // data
            var requirements = new List<IAuthorizationRequirement>
            {
                new HackathonAdministratorRequirement(),
            };
            var claims = new List<Claim>();
            var claimsPrincipal = new ClaimsPrincipal(new ClaimsIdentity(claims));
            HackathonEntity hackathonEntity = new HackathonEntity { };
            var hackathonAdminManagement = new Mock<IHackathonAdminManagement>();
            var context = new AuthorizationHandlerContext(requirements, claimsPrincipal, hackathonEntity);

            // test
            var handler = new HackathonAdministratorHandler(hackathonAdminManagement.Object);
            await handler.HandleAsync(context);

            Assert.IsFalse(context.HasSucceeded);
            Mock.VerifyAll(hackathonAdminManagement);
            hackathonAdminManagement.VerifyNoOtherCalls();
        }

        [Test]
        public async Task HandleAsyncTest_IsHackathonAdmin()
        {
            // data
            string userid = "uid";
            var requirements = new List<IAuthorizationRequirement>
            {
                new HackathonAdministratorRequirement(),
            };
            var claims = new List<Claim>
            {
                ClaimsHelper.UserId(userid),
            };
            var admins = new List<HackathonAdminEntity>
            {
                new HackathonAdminEntity{ RowKey=userid },
                new HackathonAdminEntity{ RowKey="anotherId" },
            };
            var claimsPrincipal = new ClaimsPrincipal(new ClaimsIdentity(claims));
            HackathonEntity hackathonEntity = new HackathonEntity { PartitionKey = "hack" };
            var hackathonAdminManagement = new Mock<IHackathonAdminManagement>();
            hackathonAdminManagement.Setup(h => h.ListHackathonAdminAsync("hack", CancellationToken.None))
                .ReturnsAsync(admins);
            var context = new AuthorizationHandlerContext(requirements, claimsPrincipal, hackathonEntity);

            // test
            var handler = new HackathonAdministratorHandler(hackathonAdminManagement.Object);
            await handler.HandleAsync(context);

            Assert.IsTrue(context.HasSucceeded);
            Mock.VerifyAll(hackathonAdminManagement);
            hackathonAdminManagement.VerifyNoOtherCalls();
        }

        [Test]
        public async Task HandleAsyncTest_IsNotHackathonAdmin()
        {
            // data
            string userid = "uid";
            var requirements = new List<IAuthorizationRequirement>
            {
                new HackathonAdministratorRequirement(),
            };
            var claims = new List<Claim>
            {
                ClaimsHelper.UserId(userid),
            };
            var admins = new List<HackathonAdminEntity>
            {
                new HackathonAdminEntity{ RowKey="anotherId" },
            };
            var claimsPrincipal = new ClaimsPrincipal(new ClaimsIdentity(claims));
            HackathonEntity hackathonEntity = new HackathonEntity { PartitionKey = "hack" };
            var hackathonAdminManagement = new Mock<IHackathonAdminManagement>();
            hackathonAdminManagement.Setup(h => h.ListHackathonAdminAsync("hack", CancellationToken.None))
                .ReturnsAsync(admins);
            var context = new AuthorizationHandlerContext(requirements, claimsPrincipal, hackathonEntity);

            // test
            var handler = new HackathonAdministratorHandler(hackathonAdminManagement.Object);
            await handler.HandleAsync(context);

            Assert.IsFalse(context.HasSucceeded);
            Mock.VerifyAll(hackathonAdminManagement);
            hackathonAdminManagement.VerifyNoOtherCalls();
        }
    }
}
