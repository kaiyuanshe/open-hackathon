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
    public class JudgeControllerTests
    {
        #region CreateJudge
        [Test]
        public async Task CreateJudge_UserNotFound()
        {
            var hackathon = new HackathonEntity();
            var authResult = AuthorizationResult.Success();
            var parameter = new Judge();
            UserInfo user = null;

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), hackathon, AuthConstant.Policy.HackathonAdministrator)).ReturnsAsync(authResult);
            var userManagement = new Mock<IUserManagement>();
            userManagement.Setup(u => u.GetUserByIdAsync("uid", default)).ReturnsAsync(user);

            var controller = new JudgeController
            {
                HackathonManagement = hackathonManagement.Object,
                AuthorizationService = authorizationService.Object,
                UserManagement = userManagement.Object,
            };
            var result = await controller.CreateJudge("Hack", "uid", parameter, default);

            Mock.VerifyAll(hackathonManagement, authorizationService, userManagement);
            hackathonManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();
            userManagement.VerifyNoOtherCalls();

            AssertHelper.AssertObjectResult(result, 404, Resources.User_NotFound);
        }

        [Test]
        public async Task CreateJudge_Created()
        {
            var hackathon = new HackathonEntity();
            var authResult = AuthorizationResult.Success();
            var parameter = new Judge { description = "desc" };
            UserInfo user = new UserInfo { FamilyName = "fn" };
            var entity = new JudgeEntity { PartitionKey = "pk" };

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), hackathon, AuthConstant.Policy.HackathonAdministrator)).ReturnsAsync(authResult);
            var userManagement = new Mock<IUserManagement>();
            userManagement.Setup(u => u.GetUserByIdAsync("uid", default)).ReturnsAsync(user);
            var judgeManagement = new Mock<IJudgeManagement>();
            judgeManagement.Setup(j => j.CreateJudgeAsync(It.Is<Judge>(j =>
                j.description == "desc" &&
                j.hackathonName == "hack" &&
                j.userId == "uid"), default)).ReturnsAsync(entity);

            var controller = new JudgeController
            {
                HackathonManagement = hackathonManagement.Object,
                AuthorizationService = authorizationService.Object,
                UserManagement = userManagement.Object,
                JudgeManagement = judgeManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
            };
            var result = await controller.CreateJudge("Hack", "uid", parameter, default);

            Mock.VerifyAll(hackathonManagement, authorizationService, userManagement, judgeManagement);
            hackathonManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();
            userManagement.VerifyNoOtherCalls();
            judgeManagement.VerifyNoOtherCalls();

            var resp = AssertHelper.AssertOKResult<Judge>(result);
            Assert.AreEqual("pk", resp.hackathonName);
            Assert.AreEqual("fn", resp.user.FamilyName);
        }

        #endregion
    }
}
