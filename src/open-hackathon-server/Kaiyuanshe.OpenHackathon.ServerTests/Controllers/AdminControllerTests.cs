using Kaiyuanshe.OpenHackathon.Server;
using Kaiyuanshe.OpenHackathon.Server.Auth;
using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Controllers;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.ResponseBuilder;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.AspNetCore.Authorization;
using Moq;
using NUnit.Framework;
using System.Security.Claims;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Controllers
{
    public class AdminControllerTests
    {
        #region CreateAdmin
        [Test]
        public async Task CreateAdmin_UserNotFound()
        {
            var hackathon = new HackathonEntity();
            var authResult = AuthorizationResult.Success();
            UserInfo user = null;

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), hackathon, AuthConstant.Policy.HackathonAdministrator)).ReturnsAsync(authResult);
            var userManagement = new Mock<IUserManagement>();
            userManagement.Setup(u => u.GetUserByIdAsync("uid", default)).ReturnsAsync(user);

            var controller = new AdminController
            {
                HackathonManagement = hackathonManagement.Object,
                AuthorizationService = authorizationService.Object,
                UserManagement = userManagement.Object,
            };
            var result = await controller.CreateAdmin("Hack", "uid", default);

            Mock.VerifyAll(hackathonManagement, authorizationService, userManagement);
            hackathonManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();
            userManagement.VerifyNoOtherCalls();

            AssertHelper.AssertObjectResult(result, 404, Resources.User_NotFound);
        }

        [Test]
        public async Task CreateAdmin_Succeeded()
        {
            var hackathon = new HackathonEntity();
            var authResult = AuthorizationResult.Success();
            UserInfo user = new UserInfo { Zoneinfo = "zone" };
            var adminEntity = new HackathonAdminEntity { PartitionKey = "pk", RowKey = "rk" };

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), hackathon, AuthConstant.Policy.HackathonAdministrator)).ReturnsAsync(authResult);
            var userManagement = new Mock<IUserManagement>();
            userManagement.Setup(u => u.GetUserByIdAsync("uid", default)).ReturnsAsync(user);
            var adminManagement = new Mock<IHackathonAdminManagement>();
            adminManagement.Setup(a => a.CreateAdminAsync(It.Is<HackathonAdmin>(ha =>
                ha.hackathonName == "hack" && ha.userId == "uid"), default))
                .ReturnsAsync(adminEntity);

            var controller = new AdminController
            {
                HackathonManagement = hackathonManagement.Object,
                AuthorizationService = authorizationService.Object,
                HackathonAdminManagement = adminManagement.Object,
                UserManagement = userManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
            };
            var result = await controller.CreateAdmin("Hack", "uid", default);

            Mock.VerifyAll(hackathonManagement, authorizationService, adminManagement, userManagement);
            hackathonManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();
            userManagement.VerifyNoOtherCalls();
            adminManagement.VerifyNoOtherCalls();

            var admin = AssertHelper.AssertOKResult<HackathonAdmin>(result);
            Assert.AreEqual("pk", admin.hackathonName);
            Assert.AreEqual("rk", admin.userId);
            Assert.AreEqual("zone", admin.user.Zoneinfo);
        }
        #endregion
    }
}
