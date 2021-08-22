using Kaiyuanshe.OpenHackathon.Server;
using Kaiyuanshe.OpenHackathon.Server.Auth;
using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Controllers;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.ResponseBuilder;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.AspNetCore.Authorization;
using Microsoft.WindowsAzure.Storage.Table;
using Moq;
using NUnit.Framework;
using System.Collections;
using System.Collections.Generic;
using System.Security.Claims;
using System.Threading;
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
        public async Task CreateJudge_TooMany()
        {
            var hackathon = new HackathonEntity();
            var authResult = AuthorizationResult.Success();
            var parameter = new Judge { description = "desc" };
            UserInfo user = new UserInfo { };

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), hackathon, AuthConstant.Policy.HackathonAdministrator)).ReturnsAsync(authResult);
            var userManagement = new Mock<IUserManagement>();
            userManagement.Setup(u => u.GetUserByIdAsync("uid", default)).ReturnsAsync(user);
            var judgeManagement = new Mock<IJudgeManagement>();
            judgeManagement.Setup(j => j.CanCreateJudgeAsync("hack", default)).ReturnsAsync(false);

            var controller = new JudgeController
            {
                HackathonManagement = hackathonManagement.Object,
                AuthorizationService = authorizationService.Object,
                UserManagement = userManagement.Object,
                JudgeManagement = judgeManagement.Object,
            };
            var result = await controller.CreateJudge("Hack", "uid", parameter, default);

            Mock.VerifyAll(hackathonManagement, authorizationService, userManagement, judgeManagement);
            hackathonManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();
            userManagement.VerifyNoOtherCalls();
            judgeManagement.VerifyNoOtherCalls();

            AssertHelper.AssertObjectResult(result, 412, Resources.Judge_TooMany);
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
            judgeManagement.Setup(j => j.CanCreateJudgeAsync("hack", default)).ReturnsAsync(true);

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

        #region UpdateJudge
        [Test]
        public async Task UpdateJudge_JudgeNotFound()
        {
            var hackathon = new HackathonEntity();
            var authResult = AuthorizationResult.Success();
            var parameter = new Judge();
            UserInfo user = new UserInfo();
            JudgeEntity entity = null;

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), hackathon, AuthConstant.Policy.HackathonAdministrator)).ReturnsAsync(authResult);
            var userManagement = new Mock<IUserManagement>();
            userManagement.Setup(u => u.GetUserByIdAsync("uid", default)).ReturnsAsync(user);
            var judgeManagement = new Mock<IJudgeManagement>();
            judgeManagement.Setup(j => j.GetJudgeAsync("hack", "uid", default)).ReturnsAsync(entity);

            var controller = new JudgeController
            {
                HackathonManagement = hackathonManagement.Object,
                AuthorizationService = authorizationService.Object,
                UserManagement = userManagement.Object,
                JudgeManagement = judgeManagement.Object,
            };
            var result = await controller.UpdateJudge("Hack", "uid", parameter, default);

            Mock.VerifyAll(hackathonManagement, authorizationService, userManagement, judgeManagement);
            hackathonManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();
            userManagement.VerifyNoOtherCalls();
            judgeManagement.VerifyNoOtherCalls();

            AssertHelper.AssertObjectResult(result, 404, Resources.Judge_NotFound);
        }

        [Test]
        public async Task UpdateJudge_Updated()
        {
            var hackathon = new HackathonEntity();
            var authResult = AuthorizationResult.Success();
            var parameter = new Judge();
            UserInfo user = new UserInfo { Province = "province" };
            JudgeEntity entity = new JudgeEntity { PartitionKey = "pk" };

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), hackathon, AuthConstant.Policy.HackathonAdministrator)).ReturnsAsync(authResult);
            var userManagement = new Mock<IUserManagement>();
            userManagement.Setup(u => u.GetUserByIdAsync("uid", default)).ReturnsAsync(user);
            var judgeManagement = new Mock<IJudgeManagement>();
            judgeManagement.Setup(j => j.GetJudgeAsync("hack", "uid", default)).ReturnsAsync(entity);
            judgeManagement.Setup(j => j.UpdateJudgeAsync(entity, parameter, default)).ReturnsAsync(entity);

            var controller = new JudgeController
            {
                HackathonManagement = hackathonManagement.Object,
                AuthorizationService = authorizationService.Object,
                UserManagement = userManagement.Object,
                JudgeManagement = judgeManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
            };
            var result = await controller.UpdateJudge("Hack", "uid", parameter, default);

            Mock.VerifyAll(hackathonManagement, authorizationService, userManagement, judgeManagement);
            hackathonManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();
            userManagement.VerifyNoOtherCalls();
            judgeManagement.VerifyNoOtherCalls();

            var resp = AssertHelper.AssertOKResult<Judge>(result);
            Assert.AreEqual("pk", resp.hackathonName);
            Assert.AreEqual("province", resp.user.Province);
        }

        #endregion

        #region GetJudge
        [Test]
        public async Task GetJudge_HackNotOnline()
        {
            var hackathon = new HackathonEntity { };

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);

            var controller = new JudgeController
            {
                HackathonManagement = hackathonManagement.Object,
            };
            var result = await controller.GetJudge("Hack", "uid", default);

            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();

            AssertHelper.AssertObjectResult(result, 404, string.Format(Resources.Hackathon_NotFound, "Hack"));
        }

        [Test]
        public async Task GetJudge_NotFound()
        {
            var hackathon = new HackathonEntity { Status = HackathonStatus.online };
            UserInfo user = null;

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);
            var userManagement = new Mock<IUserManagement>();
            userManagement.Setup(u => u.GetUserByIdAsync("uid", default)).ReturnsAsync(user);

            var controller = new JudgeController
            {
                HackathonManagement = hackathonManagement.Object,
                UserManagement = userManagement.Object,
            };
            var result = await controller.GetJudge("Hack", "uid", default);

            Mock.VerifyAll(hackathonManagement, userManagement);
            hackathonManagement.VerifyNoOtherCalls();
            userManagement.VerifyNoOtherCalls();

            AssertHelper.AssertObjectResult(result, 404, Resources.User_NotFound);
        }
        [Test]
        public async Task GetJudge_Succeeded()
        {
            var hackathon = new HackathonEntity { Status = HackathonStatus.online };
            UserInfo user = new UserInfo { Profile = "profile" };
            var judgeEntity = new JudgeEntity { PartitionKey = "pk" };

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);
            var userManagement = new Mock<IUserManagement>();
            userManagement.Setup(u => u.GetUserByIdAsync("uid", default)).ReturnsAsync(user);
            var judgeManagement = new Mock<IJudgeManagement>();
            judgeManagement.Setup(j => j.GetJudgeAsync("hack", "uid", default)).ReturnsAsync(judgeEntity);

            var controller = new JudgeController
            {
                HackathonManagement = hackathonManagement.Object,
                UserManagement = userManagement.Object,
                JudgeManagement = judgeManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
            };
            var result = await controller.GetJudge("Hack", "uid", default);

            Mock.VerifyAll(hackathonManagement, userManagement, judgeManagement);
            hackathonManagement.VerifyNoOtherCalls();
            userManagement.VerifyNoOtherCalls();
            judgeManagement.VerifyNoOtherCalls();

            var resp = AssertHelper.AssertOKResult<Judge>(result);
            Assert.AreEqual("pk", resp.hackathonName);
            Assert.AreEqual("profile", resp.user.Profile);
        }

        #endregion

        #region ListJudgesByHackathon
        private static IEnumerable ListJudgesByHackathonTestData()
        {
            // arg0: pagination
            // arg1: next TableCotinuationToken
            // arg2: expected nextlink

            // no pagination, no filter, no top
            yield return new TestCaseData(
                    new Pagination { },
                    null,
                    null
                );

            // with pagination and filters
            yield return new TestCaseData(
                    new Pagination { top = 10, np = "np", nr = "nr" },
                    null,
                    null
                );

            // next link
            yield return new TestCaseData(
                    new Pagination { },
                    new TableContinuationToken
                    {
                        NextPartitionKey = "np",
                        NextRowKey = "nr"
                    },
                    "&np=np&nr=nr"
                );

            // next link with top
            yield return new TestCaseData(
                    new Pagination { top = 10, np = "np", nr = "nr" },
                    new TableContinuationToken
                    {
                        NextPartitionKey = "np2",
                        NextRowKey = "nr2"
                    },
                    "&top=10&np=np2&nr=nr2"
                );
        }

        [Test, TestCaseSource(nameof(ListJudgesByHackathonTestData))]
        public async Task ListJudgesByHackathon(
            Pagination pagination,
            TableContinuationToken next,
            string expectedLink)
        {
            // input
            HackathonEntity hackathon = new HackathonEntity();
            List<JudgeEntity> judges = new List<JudgeEntity> {
                new JudgeEntity { PartitionKey = "pk", RowKey = "uid" }
            };
            var user = new UserInfo { Website = "https://website" };

            // mock and capture
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);
            var judgeManagement = new Mock<IJudgeManagement>();
            judgeManagement.Setup(j => j.ListPaginatedJudgesAsync("hack", It.Is<JudgeQueryOptions>(o => o.Top == pagination.top), default))
                .Callback<string, JudgeQueryOptions, CancellationToken>((h, opt, c) => { opt.Next = next; })
                .ReturnsAsync(judges);
            var userManagement = new Mock<IUserManagement>();
            userManagement.Setup(u => u.GetUserByIdAsync("uid", default)).ReturnsAsync(user);

            // run
            var controller = new JudgeController
            {
                ResponseBuilder = new DefaultResponseBuilder(),
                HackathonManagement = hackathonManagement.Object,
                UserManagement = userManagement.Object,
                JudgeManagement = judgeManagement.Object,
            };
            var result = await controller.ListJudgesByHackathon("Hack", pagination, default);

            // verify
            Mock.VerifyAll(hackathonManagement, judgeManagement, userManagement);
            hackathonManagement.VerifyNoOtherCalls();
            judgeManagement.VerifyNoOtherCalls();
            userManagement.VerifyNoOtherCalls();

            var list = AssertHelper.AssertOKResult<JudgeList>(result);
            Assert.AreEqual(expectedLink, list.nextLink);
            Assert.AreEqual(1, list.value.Length);
            Assert.AreEqual("pk", list.value[0].hackathonName);
            Assert.AreEqual("uid", list.value[0].userId);
            Assert.AreEqual("https://website", list.value[0].user.Website);
        }
        #endregion

        #region DeleteJudge
        [TestCase(false)]
        [TestCase(true)]
        public async Task DeleteJudge(bool firstTime)
        {
            var hackathon = new HackathonEntity();
            var authResult = AuthorizationResult.Success();
            UserInfo user = new UserInfo { };
            JudgeEntity entity = firstTime ? new JudgeEntity() : null;

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), hackathon, AuthConstant.Policy.HackathonAdministrator)).ReturnsAsync(authResult);
            var userManagement = new Mock<IUserManagement>();
            userManagement.Setup(u => u.GetUserByIdAsync("uid", default)).ReturnsAsync(user);
            var judgeManagement = new Mock<IJudgeManagement>();
            judgeManagement.Setup(j => j.GetJudgeAsync("hack", "uid", default)).ReturnsAsync(entity);
            var ratingManagement = new Mock<IRatingManagement>();
            if (firstTime)
            {
                judgeManagement.Setup(j => j.DeleteJudgeAsync("hack", "uid", default));
                ratingManagement.Setup(j => j.IsRatingCountGreaterThanZero(
                        "hack",
                        It.Is<RatingQueryOptions>(o => o.RatingKindId == null && o.JudgeId == "uid" && o.TeamId == null),
                        default)).ReturnsAsync(false);
            }

            var controller = new JudgeController
            {
                HackathonManagement = hackathonManagement.Object,
                AuthorizationService = authorizationService.Object,
                UserManagement = userManagement.Object,
                JudgeManagement = judgeManagement.Object,
                RatingManagement = ratingManagement.Object,
            };
            var result = await controller.DeleteJudge("Hack", "uid", default);

            Mock.VerifyAll(hackathonManagement, authorizationService, userManagement, judgeManagement, ratingManagement);
            hackathonManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();
            userManagement.VerifyNoOtherCalls();
            judgeManagement.VerifyNoOtherCalls();
            ratingManagement.VerifyNoOtherCalls();

            AssertHelper.AssertNoContentResult(result);
        }

        [Test]
        public async Task DeleteJudge_HasRating()
        {
            var hackathon = new HackathonEntity();
            var authResult = AuthorizationResult.Success();
            UserInfo user = new UserInfo { };
            JudgeEntity entity = new JudgeEntity();

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), hackathon, AuthConstant.Policy.HackathonAdministrator)).ReturnsAsync(authResult);
            var userManagement = new Mock<IUserManagement>();
            userManagement.Setup(u => u.GetUserByIdAsync("uid", default)).ReturnsAsync(user);
            var judgeManagement = new Mock<IJudgeManagement>();
            judgeManagement.Setup(j => j.GetJudgeAsync("hack", "uid", default)).ReturnsAsync(entity);
            var ratingManagement = new Mock<IRatingManagement>();
            ratingManagement.Setup(j => j.IsRatingCountGreaterThanZero(
                "hack",
                It.Is<RatingQueryOptions>(o => o.RatingKindId == null && o.JudgeId == "uid" && o.TeamId == null),
                default)).ReturnsAsync(true);

            var controller = new JudgeController
            {
                HackathonManagement = hackathonManagement.Object,
                AuthorizationService = authorizationService.Object,
                UserManagement = userManagement.Object,
                JudgeManagement = judgeManagement.Object,
                RatingManagement = ratingManagement.Object,
            };
            var result = await controller.DeleteJudge("Hack", "uid", default);

            Mock.VerifyAll(hackathonManagement, authorizationService, userManagement, judgeManagement, ratingManagement);
            hackathonManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();
            userManagement.VerifyNoOtherCalls();
            judgeManagement.VerifyNoOtherCalls();
            ratingManagement.VerifyNoOtherCalls();

            AssertHelper.AssertObjectResult(result, 412, string.Format(Resources.Rating_HasRating, nameof(Judge)));
        }
        #endregion
    }
}
