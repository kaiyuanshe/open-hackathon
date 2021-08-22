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
    public class RatingControllerTests
    {
        #region CreateRatingKind
        [Test]
        public async Task CreateRatingKind_TooMany()
        {
            // input
            string hackName = "Hack";
            HackathonEntity hackathon = new HackathonEntity { };
            RatingKind parameter = new RatingKind { };
            var authResult = AuthorizationResult.Success();

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), hackathon, AuthConstant.Policy.HackathonAdministrator))
                .ReturnsAsync(authResult);
            var ratingManagement = new Mock<IRatingManagement>();
            ratingManagement.Setup(t => t.CanCreateRatingKindAsync("hack", default)).ReturnsAsync(false);

            // run
            var controller = new RatingController
            {
                HackathonManagement = hackathonManagement.Object,
                RatingManagement = ratingManagement.Object,
                AuthorizationService = authorizationService.Object,
            };
            var result = await controller.CreateRatingKind(hackName, parameter, default);

            // verify
            Mock.VerifyAll(hackathonManagement, ratingManagement, authorizationService);
            hackathonManagement.VerifyNoOtherCalls();
            ratingManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();

            AssertHelper.AssertObjectResult(result, 412, Resources.Rating_TooManyKinds);
        }

        [Test]
        public async Task CreateRatingKind()
        {
            // input
            string hackName = "Hack";
            HackathonEntity hackathon = new HackathonEntity { };
            RatingKind parameter = new RatingKind { };
            RatingKindEntity ratingKindEntity = new RatingKindEntity
            {
                Name = "n",
                PartitionKey = "pk",
                RowKey = "rk",
                Description = "desc",
                MaximumScore = 5,
            };
            var authResult = AuthorizationResult.Success();

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), hackathon, AuthConstant.Policy.HackathonAdministrator))
                .ReturnsAsync(authResult);
            var ratingManagement = new Mock<IRatingManagement>();
            ratingManagement.Setup(t => t.CreateRatingKindAsync(parameter, default)).ReturnsAsync(ratingKindEntity);
            ratingManagement.Setup(t => t.CanCreateRatingKindAsync("hack", default)).ReturnsAsync(true);

            // run
            var controller = new RatingController
            {
                HackathonManagement = hackathonManagement.Object,
                RatingManagement = ratingManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
                AuthorizationService = authorizationService.Object,
            };
            var result = await controller.CreateRatingKind(hackName, parameter, default);

            // verify
            Mock.VerifyAll(hackathonManagement, ratingManagement, authorizationService);
            hackathonManagement.VerifyNoOtherCalls();
            ratingManagement.Verify(r => r.CreateRatingKindAsync(It.Is<RatingKind>(p => p.hackathonName == "hack"), default));
            ratingManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();

            RatingKind resp = AssertHelper.AssertOKResult<RatingKind>(result);
            Assert.AreEqual("desc", resp.description);
            Assert.AreEqual("pk", resp.hackathonName);
            Assert.AreEqual("rk", resp.id);
            Assert.AreEqual("n", resp.name);
            Assert.AreEqual(5, resp.maximumScore);
        }
        #endregion

        #region UpdateRatingKind
        [Test]
        public async Task UpdateRatingKind_KindNotFound()
        {
            var hackathon = new HackathonEntity();
            var authResult = AuthorizationResult.Success();
            var parameter = new RatingKind();
            RatingKindEntity entity = null;

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), hackathon, AuthConstant.Policy.HackathonAdministrator)).ReturnsAsync(authResult);
            var ratingManagement = new Mock<IRatingManagement>();
            ratingManagement.Setup(j => j.GetRatingKindAsync("hack", "kid", default)).ReturnsAsync(entity);

            var controller = new RatingController
            {
                HackathonManagement = hackathonManagement.Object,
                AuthorizationService = authorizationService.Object,
                RatingManagement = ratingManagement.Object,
            };
            var result = await controller.UpdateRatingKind("Hack", "kid", parameter, default);

            Mock.VerifyAll(hackathonManagement, authorizationService, ratingManagement);
            hackathonManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();
            ratingManagement.VerifyNoOtherCalls();

            AssertHelper.AssertObjectResult(result, 404, Resources.Rating_KindNotFound);
        }

        [Test]
        public async Task UpdateRatingKind_Updated()
        {
            var hackathon = new HackathonEntity();
            var authResult = AuthorizationResult.Success();
            var parameter = new RatingKind();
            RatingKindEntity entity = new RatingKindEntity { PartitionKey = "pk" };

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), hackathon, AuthConstant.Policy.HackathonAdministrator)).ReturnsAsync(authResult);
            var ratingManagement = new Mock<IRatingManagement>();
            ratingManagement.Setup(r => r.GetRatingKindAsync("hack", "kid", default)).ReturnsAsync(entity);
            ratingManagement.Setup(r => r.UpdateRatingKindAsync(entity, parameter, default)).ReturnsAsync(entity);

            var controller = new RatingController
            {
                HackathonManagement = hackathonManagement.Object,
                AuthorizationService = authorizationService.Object,
                RatingManagement = ratingManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
            };
            var result = await controller.UpdateRatingKind("Hack", "kid", parameter, default);

            Mock.VerifyAll(hackathonManagement, authorizationService, ratingManagement);
            hackathonManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();
            ratingManagement.VerifyNoOtherCalls();

            var resp = AssertHelper.AssertOKResult<RatingKind>(result);
            Assert.AreEqual("pk", resp.hackathonName);
        }
        #endregion

        #region GetRatingKind
        [Test]
        public async Task GetRatingKind_NotFound()
        {
            // input
            HackathonEntity hackathon = new HackathonEntity { };
            RatingKindEntity ratingKindEntity = null;

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);
            var ratingManagement = new Mock<IRatingManagement>();
            ratingManagement.Setup(t => t.GetRatingKindAsync("hack", "kid", default)).ReturnsAsync(ratingKindEntity);

            // run
            var controller = new RatingController
            {
                HackathonManagement = hackathonManagement.Object,
                RatingManagement = ratingManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
            };
            var result = await controller.GetRatingKind("HACK", "kid", default);

            // verify
            Mock.VerifyAll(hackathonManagement, ratingManagement);
            hackathonManagement.VerifyNoOtherCalls();
            ratingManagement.VerifyNoOtherCalls();

            AssertHelper.AssertObjectResult(result, 404, Resources.Rating_KindNotFound);
        }

        [Test]
        public async Task GetRatingKind_Succedded()
        {
            // input
            HackathonEntity hackathon = new HackathonEntity { };
            RatingKindEntity ratingKindEntity = new RatingKindEntity { RowKey = "rk" };

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);
            var ratingManagement = new Mock<IRatingManagement>();
            ratingManagement.Setup(t => t.GetRatingKindAsync("hack", "kid", default)).ReturnsAsync(ratingKindEntity);

            // run
            var controller = new RatingController
            {
                HackathonManagement = hackathonManagement.Object,
                RatingManagement = ratingManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
            };
            var result = await controller.GetRatingKind("HACK", "kid", default);

            // verify
            Mock.VerifyAll(hackathonManagement, ratingManagement);
            hackathonManagement.VerifyNoOtherCalls();
            ratingManagement.VerifyNoOtherCalls();

            RatingKind resp = AssertHelper.AssertOKResult<RatingKind>(result);
            Assert.AreEqual("rk", resp.id);
        }
        #endregion

        #region ListRatingKinds
        private static IEnumerable ListRatingKindsTestData()
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

        [Test, TestCaseSource(nameof(ListRatingKindsTestData))]
        public async Task ListRatingKinds(
            Pagination pagination,
            TableContinuationToken next,
            string expectedLink)
        {
            // input
            var hackName = "Hack";
            HackathonEntity hackathonEntity = new HackathonEntity();
            var awards = new List<RatingKindEntity>
            {
                new RatingKindEntity
                {
                    PartitionKey = "pk",
                    RowKey = "rk",
                }
            };

            // mock and capture
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default))
                .ReturnsAsync(hackathonEntity);
            var ratingManagement = new Mock<IRatingManagement>();
            ratingManagement.Setup(p => p.ListPaginatedRatingKindsAsync("hack", It.IsAny<RatingKindQueryOptions>(), default))
                .Callback<string, RatingKindQueryOptions, CancellationToken>((n, o, t) =>
                {
                    o.Next = next;
                })
                .ReturnsAsync(awards);

            // run
            var controller = new RatingController
            {
                ResponseBuilder = new DefaultResponseBuilder(),
                HackathonManagement = hackathonManagement.Object,
                RatingManagement = ratingManagement.Object,
            };
            var result = await controller.ListRatingKinds(hackName, pagination, default);

            // verify
            Mock.VerifyAll(hackathonManagement, ratingManagement);
            hackathonManagement.VerifyNoOtherCalls();
            ratingManagement.VerifyNoOtherCalls();

            var list = AssertHelper.AssertOKResult<RatingKindList>(result);
            Assert.AreEqual(expectedLink, list.nextLink);
            Assert.AreEqual(1, list.value.Length);
            Assert.AreEqual("pk", list.value[0].hackathonName);
            Assert.AreEqual("rk", list.value[0].id);
        }
        #endregion

        #region DeleteRatingKind
        [TestCase(false)]
        [TestCase(true)]
        public async Task DeleteRatingKind(bool firstTime)
        {
            var hackathon = new HackathonEntity();
            var authResult = AuthorizationResult.Success();
            RatingKindEntity entity = firstTime ? new RatingKindEntity { RowKey = "kid" } : null;

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), hackathon, AuthConstant.Policy.HackathonAdministrator)).ReturnsAsync(authResult);
            var ratingManagement = new Mock<IRatingManagement>();
            ratingManagement.Setup(j => j.GetRatingKindAsync("hack", "kid", default)).ReturnsAsync(entity);
            if (firstTime)
            {
                ratingManagement.Setup(j => j.IsRatingCountGreaterThanZero(
                    "hack",
                    It.Is<RatingQueryOptions>(o => o.RatingKindId == "kid" && o.JudgeId == null && o.TeamId == null),
                    default)).ReturnsAsync(false);
                ratingManagement.Setup(j => j.DeleteRatingKindAsync("hack", "kid", default));
            }

            var controller = new RatingController
            {
                HackathonManagement = hackathonManagement.Object,
                AuthorizationService = authorizationService.Object,
                RatingManagement = ratingManagement.Object,
            };
            var result = await controller.DeleteRatingKind("Hack", "kid", default);

            Mock.VerifyAll(hackathonManagement, authorizationService, ratingManagement);
            hackathonManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();
            ratingManagement.VerifyNoOtherCalls();

            AssertHelper.AssertNoContentResult(result);
        }

        [Test]
        public async Task DeleteRatingKind_HasRating()
        {
            var hackathon = new HackathonEntity();
            var authResult = AuthorizationResult.Success();
            RatingKindEntity entity = new RatingKindEntity { RowKey = "kid" };

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), hackathon, AuthConstant.Policy.HackathonAdministrator)).ReturnsAsync(authResult);
            var ratingManagement = new Mock<IRatingManagement>();
            ratingManagement.Setup(j => j.GetRatingKindAsync("hack", "kid", default)).ReturnsAsync(entity);
            ratingManagement.Setup(j => j.IsRatingCountGreaterThanZero(
                "hack",
                It.Is<RatingQueryOptions>(o => o.RatingKindId == "kid" && o.JudgeId == null && o.TeamId == null),
                default)).ReturnsAsync(true);

            var controller = new RatingController
            {
                HackathonManagement = hackathonManagement.Object,
                AuthorizationService = authorizationService.Object,
                RatingManagement = ratingManagement.Object,
            };
            var result = await controller.DeleteRatingKind("Hack", "kid", default);

            Mock.VerifyAll(hackathonManagement, authorizationService, ratingManagement);
            hackathonManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();
            ratingManagement.VerifyNoOtherCalls();

            AssertHelper.AssertObjectResult(result, 412, string.Format(Resources.Rating_HasRating, nameof(RatingKind)));
        }
        #endregion

        #region CreateRating
        [Test]
        public async Task CreateRating_NotJudge()
        {
            // data
            Rating parameter = new Rating { };
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            var authResult = AuthorizationResult.Failed();

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), hackathon, AuthConstant.Policy.HackathonJudge))
               .ReturnsAsync(authResult);

            // test
            var controller = new RatingController
            {
                HackathonManagement = hackathonManagement.Object,
                AuthorizationService = authorizationService.Object
            };
            var result = await controller.CreateRating("Hack", parameter, default);

            // verify
            Mock.VerifyAll(hackathonManagement, authorizationService);
            hackathonManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();

            AssertHelper.AssertObjectResult(result, 403, Resources.Hackathon_NotJudge);
        }

        [Test]
        public async Task CreateRating_TeamNotFound()
        {
            // data
            Rating parameter = new Rating { teamId = "tid" };
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            var authResult = AuthorizationResult.Success();
            TeamEntity team = null;

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), hackathon, AuthConstant.Policy.HackathonJudge))
               .ReturnsAsync(authResult);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("hack", "tid", default)).ReturnsAsync(team);

            // test
            var controller = new RatingController
            {
                HackathonManagement = hackathonManagement.Object,
                AuthorizationService = authorizationService.Object,
                TeamManagement = teamManagement.Object,
            };
            var result = await controller.CreateRating("Hack", parameter, default);

            // verify
            Mock.VerifyAll(hackathonManagement, authorizationService, teamManagement);
            hackathonManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();

            AssertHelper.AssertObjectResult(result, 404, Resources.Team_NotFound);
        }

        [Test]
        public async Task CreateRating_KindNotFound()
        {
            // data
            Rating parameter = new Rating { teamId = "tid", ratingKindId = "kid" };
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            var authResult = AuthorizationResult.Success();
            TeamEntity team = new TeamEntity { };
            RatingKindEntity ratingKind = null;

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), hackathon, AuthConstant.Policy.HackathonJudge))
               .ReturnsAsync(authResult);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("hack", "tid", default)).ReturnsAsync(team);
            var ratingManagement = new Mock<IRatingManagement>();
            ratingManagement.Setup(j => j.GetRatingKindAsync("hack", "kid", default)).ReturnsAsync(ratingKind);

            // test
            var controller = new RatingController
            {
                HackathonManagement = hackathonManagement.Object,
                AuthorizationService = authorizationService.Object,
                TeamManagement = teamManagement.Object,
                RatingManagement = ratingManagement.Object,
            };
            var result = await controller.CreateRating("Hack", parameter, default);

            // verify
            Mock.VerifyAll(hackathonManagement, authorizationService, teamManagement, ratingManagement);
            hackathonManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            ratingManagement.VerifyNoOtherCalls();

            AssertHelper.AssertObjectResult(result, 404, Resources.Rating_KindNotFound);
        }

        [Test]
        public async Task CreateRating_ScoreOutOfRange()
        {
            // data
            Rating parameter = new Rating { teamId = "tid", ratingKindId = "kid", score = 4 };
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            var authResult = AuthorizationResult.Success();
            TeamEntity team = new TeamEntity { };
            RatingKindEntity ratingKind = new RatingKindEntity { MaximumScore = 3 };

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), hackathon, AuthConstant.Policy.HackathonJudge))
               .ReturnsAsync(authResult);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("hack", "tid", default)).ReturnsAsync(team);
            var ratingManagement = new Mock<IRatingManagement>();
            ratingManagement.Setup(j => j.GetRatingKindAsync("hack", "kid", default)).ReturnsAsync(ratingKind);

            // test
            var controller = new RatingController
            {
                HackathonManagement = hackathonManagement.Object,
                AuthorizationService = authorizationService.Object,
                TeamManagement = teamManagement.Object,
                RatingManagement = ratingManagement.Object,
            };
            var result = await controller.CreateRating("Hack", parameter, default);

            // verify
            Mock.VerifyAll(hackathonManagement, authorizationService, teamManagement, ratingManagement);
            hackathonManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            ratingManagement.VerifyNoOtherCalls();

            AssertHelper.AssertObjectResult(result, 400, string.Format(Resources.Rating_ScoreNotInRange, ratingKind.MaximumScore));
        }

        [Test]
        public async Task CreateRating_Succeeded()
        {
            // data
            Rating parameter = new Rating { teamId = "tid", ratingKindId = "kid", score = 4 };
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            var authResult = AuthorizationResult.Success();
            TeamEntity team = new TeamEntity { CreatorId = "creator" };
            RatingKindEntity ratingKind = new RatingKindEntity { MaximumScore = 4 };
            RatingEntity ratingEntity = new RatingEntity { JudgeId = "judge", Description = "desc" };
            UserInfo judge = new UserInfo { Username = "un" };
            UserInfo teamCreator = new UserInfo { Phone = "phone" };

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), hackathon, AuthConstant.Policy.HackathonJudge))
               .ReturnsAsync(authResult);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("hack", "tid", default)).ReturnsAsync(team);
            var ratingManagement = new Mock<IRatingManagement>();
            ratingManagement.Setup(j => j.GetRatingKindAsync("hack", "kid", default)).ReturnsAsync(ratingKind);
            ratingManagement.Setup(j => j.CreateRatingAsync(It.Is<Rating>(p =>
                  p.hackathonName == "hack" &&
                  p.judgeId == ""
            ), default)).ReturnsAsync(ratingEntity);
            var userManagement = new Mock<IUserManagement>();
            userManagement.Setup(u => u.GetUserByIdAsync("judge", default)).ReturnsAsync(judge);
            userManagement.Setup(u => u.GetUserByIdAsync("creator", default)).ReturnsAsync(teamCreator);

            // test
            var controller = new RatingController
            {
                HackathonManagement = hackathonManagement.Object,
                AuthorizationService = authorizationService.Object,
                TeamManagement = teamManagement.Object,
                RatingManagement = ratingManagement.Object,
                UserManagement = userManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
            };
            var result = await controller.CreateRating("Hack", parameter, default);

            // verify
            Mock.VerifyAll(hackathonManagement, authorizationService, teamManagement, ratingManagement, userManagement);
            hackathonManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            ratingManagement.VerifyNoOtherCalls();
            userManagement.VerifyNoOtherCalls();

            var resp = AssertHelper.AssertOKResult<Rating>(result);
            Assert.AreEqual("desc", resp.description);
            Assert.AreEqual("phone", resp.team.creator.Phone);
            Assert.AreEqual("un", resp.judge.Username);
            Assert.AreEqual(4, resp.ratingKind.maximumScore);
        }
        #endregion

        #region UpdateRating
        [Test]
        public async Task UpdateRating_RatingNotFound()
        {
            // data
            Rating parameter = new Rating { description = "d2" };
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            var authResult = AuthorizationResult.Success();
            RatingEntity ratingEntity = null;

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), hackathon, AuthConstant.Policy.HackathonJudge))
               .ReturnsAsync(authResult);
            var ratingManagement = new Mock<IRatingManagement>();
            ratingManagement.Setup(j => j.GetRatingAsync("hack", "rid", default)).ReturnsAsync(ratingEntity);

            // test
            var controller = new RatingController
            {
                HackathonManagement = hackathonManagement.Object,
                AuthorizationService = authorizationService.Object,
                RatingManagement = ratingManagement.Object,
            };
            var result = await controller.UpdateRating("Hack", "rid", parameter, default);

            // verify
            Mock.VerifyAll(hackathonManagement, authorizationService, ratingManagement);
            hackathonManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();
            ratingManagement.VerifyNoOtherCalls();

            AssertHelper.AssertObjectResult(result, 404, Resources.Rating_NotFound);
        }

        [Test]
        public async Task UpdateRating_CreatedByOthers()
        {
            // data
            Rating parameter = new Rating { description = "d2" };
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            var authResult = AuthorizationResult.Success();
            RatingEntity ratingEntity = new RatingEntity { JudgeId = "anotherUser" };

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), hackathon, AuthConstant.Policy.HackathonJudge))
               .ReturnsAsync(authResult);
            var ratingManagement = new Mock<IRatingManagement>();
            ratingManagement.Setup(j => j.GetRatingAsync("hack", "rid", default)).ReturnsAsync(ratingEntity);
            var adminManagement = new Mock<IHackathonAdminManagement>();
            adminManagement.Setup(a => a.IsHackathonAdmin("hack", It.IsAny<ClaimsPrincipal>(), default)).ReturnsAsync(false);

            // test
            var controller = new RatingController
            {
                HackathonManagement = hackathonManagement.Object,
                AuthorizationService = authorizationService.Object,
                RatingManagement = ratingManagement.Object,
                HackathonAdminManagement = adminManagement.Object,
            };
            var result = await controller.UpdateRating("Hack", "rid", parameter, default);

            // verify
            Mock.VerifyAll(hackathonManagement, authorizationService, ratingManagement, adminManagement);
            hackathonManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();
            ratingManagement.VerifyNoOtherCalls();
            adminManagement.VerifyNoOtherCalls();

            AssertHelper.AssertObjectResult(result, 403, Resources.Rating_OnlyCreator);
        }

        [Test]
        public async Task UpdateRating_ScoreOutOfRange()
        {
            // data
            Rating parameter = new Rating { description = "d2", score = 6 };
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            var authResult = AuthorizationResult.Success();
            RatingEntity ratingEntity = new RatingEntity { JudgeId = "anotherUser", Score = 4, RatingKindId = "kid" };
            RatingKindEntity ratingKindEntity = new RatingKindEntity { MaximumScore = 5 };

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), hackathon, AuthConstant.Policy.HackathonJudge))
               .ReturnsAsync(authResult);
            var ratingManagement = new Mock<IRatingManagement>();
            ratingManagement.Setup(r => r.GetRatingAsync("hack", "rid", default)).ReturnsAsync(ratingEntity);
            ratingManagement.Setup(r => r.GetRatingKindAsync("hack", "kid", default)).ReturnsAsync(ratingKindEntity);
            var adminManagement = new Mock<IHackathonAdminManagement>();
            adminManagement.Setup(a => a.IsHackathonAdmin("hack", It.IsAny<ClaimsPrincipal>(), default)).ReturnsAsync(true);

            // test
            var controller = new RatingController
            {
                HackathonManagement = hackathonManagement.Object,
                AuthorizationService = authorizationService.Object,
                RatingManagement = ratingManagement.Object,
                HackathonAdminManagement = adminManagement.Object,
            };
            var result = await controller.UpdateRating("Hack", "rid", parameter, default);

            // verify
            Mock.VerifyAll(hackathonManagement, authorizationService, ratingManagement, adminManagement);
            hackathonManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();
            ratingManagement.VerifyNoOtherCalls();
            adminManagement.VerifyNoOtherCalls();

            AssertHelper.AssertObjectResult(result, 400, string.Format(Resources.Rating_ScoreNotInRange, ratingKindEntity.MaximumScore));
        }

        [Test]
        public async Task UpdateRating_Succeeded()
        {
            // data
            Rating parameter = new Rating { description = "d2" };
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            var authResult = AuthorizationResult.Success();
            RatingEntity ratingEntity = new RatingEntity { JudgeId = "anotherUser", Score = 4, RatingKindId = "kid", TeamId = "tid", PartitionKey = "hack" };
            RatingKindEntity ratingKindEntity = new RatingKindEntity { MaximumScore = 5 };
            TeamEntity team = new TeamEntity { CreatorId = "creator" };
            UserInfo judge = new UserInfo { Nickname = "nickname" };
            UserInfo teamCreator = new UserInfo { Photo = "photo" };

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), hackathon, AuthConstant.Policy.HackathonJudge))
               .ReturnsAsync(authResult);
            var ratingManagement = new Mock<IRatingManagement>();
            ratingManagement.Setup(r => r.GetRatingAsync("hack", "rid", default)).ReturnsAsync(ratingEntity);
            ratingManagement.Setup(r => r.GetRatingKindAsync("hack", "kid", default)).ReturnsAsync(ratingKindEntity);
            ratingManagement.Setup(r => r.UpdateRatingAsync(ratingEntity, parameter, default)).ReturnsAsync(ratingEntity);
            var adminManagement = new Mock<IHackathonAdminManagement>();
            adminManagement.Setup(a => a.IsHackathonAdmin("hack", It.IsAny<ClaimsPrincipal>(), default)).ReturnsAsync(true);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("hack", "tid", default)).ReturnsAsync(team);
            var userManagement = new Mock<IUserManagement>();
            userManagement.Setup(u => u.GetUserByIdAsync("anotherUser", default)).ReturnsAsync(judge);
            userManagement.Setup(u => u.GetUserByIdAsync("creator", default)).ReturnsAsync(teamCreator);

            // test
            var controller = new RatingController
            {
                HackathonManagement = hackathonManagement.Object,
                AuthorizationService = authorizationService.Object,
                RatingManagement = ratingManagement.Object,
                HackathonAdminManagement = adminManagement.Object,
                TeamManagement = teamManagement.Object,
                UserManagement = userManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
            };
            var result = await controller.UpdateRating("Hack", "rid", parameter, default);

            // verify
            Mock.VerifyAll(hackathonManagement, authorizationService, ratingManagement, adminManagement, teamManagement, userManagement);
            hackathonManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();
            ratingManagement.VerifyNoOtherCalls();
            adminManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            userManagement.VerifyNoOtherCalls();

            var resp = AssertHelper.AssertOKResult<Rating>(result);
            Assert.AreEqual(4, resp.score);
            Assert.AreEqual("photo", resp.team.creator.Photo);
            Assert.AreEqual("nickname", resp.judge.Nickname);
            Assert.AreEqual(5, resp.ratingKind.maximumScore);
        }
        #endregion

        #region ListPaginatedRatings
        private static IEnumerable ListPaginatedRatingsTestData()
        {
            // arg0: pagination
            // arg1: mocked next TableCotinuationToken
            // arg2: kindId
            // arg3: teamId
            // arg4: judgeId
            // arg5: expected options
            // arg6: expected nextlink

            // no pagination, no filter, no top
            yield return new TestCaseData(
                    new Pagination { },
                    null,
                    null,
                    null,
                    null,
                    new RatingQueryOptions { },
                    null
                );

            // with pagination
            yield return new TestCaseData(
                    new Pagination { top = 10, np = "np", nr = "nr" },
                    null,
                    null,
                    null,
                    null,
                    new RatingQueryOptions
                    {
                        Top = 10,
                        TableContinuationToken = new TableContinuationToken
                        {
                            NextPartitionKey = "np",
                            NextRowKey = "nr"
                        },
                    },
                    null
                );

            // next page
            yield return new TestCaseData(
                    new Pagination { },
                    new TableContinuationToken
                    {
                        NextPartitionKey = "np",
                        NextRowKey = "nr"
                    },
                    null,
                    null,
                    null,
                    new RatingQueryOptions { },
                    "&np=np&nr=nr"
                );

            // filter: kindId
            yield return new TestCaseData(
                    new Pagination { },
                    new TableContinuationToken
                    {
                        NextPartitionKey = "np",
                        NextRowKey = "nr"
                    },
                    "kid",
                    null,
                    null,
                    new RatingQueryOptions { RatingKindId = "kid" },
                    "&ratingKindId=kid&np=np&nr=nr"
                );

            // filter: teamId
            yield return new TestCaseData(
                    new Pagination { },
                    new TableContinuationToken
                    {
                        NextPartitionKey = "np",
                        NextRowKey = "nr"
                    },
                    null,
                    "tid",
                    null,
                    new RatingQueryOptions { TeamId = "tid" },
                    "&teamId=tid&np=np&nr=nr"
                );

            // filter: judgeId
            yield return new TestCaseData(
                    new Pagination { },
                    new TableContinuationToken
                    {
                        NextPartitionKey = "np",
                        NextRowKey = "nr"
                    },
                    null,
                    null,
                    "jid",
                    new RatingQueryOptions { JudgeId = "jid" },
                    "&judgeId=jid&np=np&nr=nr"
                );

            // all
            yield return new TestCaseData(
                    new Pagination { top = 10, np = "np", nr = "nr" },
                    new TableContinuationToken
                    {
                        NextPartitionKey = "np",
                        NextRowKey = "nr"
                    },
                    "kid",
                    "tid",
                    "jid",
                    new RatingQueryOptions
                    {
                        Top = 10,
                        TableContinuationToken = new TableContinuationToken
                        {
                            NextPartitionKey = "np",
                            NextRowKey = "nr"
                        },
                        JudgeId = "jid",
                        TeamId = "tid",
                        RatingKindId = "kid",
                    },
                    "&top=10&ratingKindId=kid&teamId=tid&judgeId=jid&np=np&nr=nr"
                );
        }

        [Test, TestCaseSource(nameof(ListPaginatedRatingsTestData))]
        public async Task ListPaginatedRatings(
            Pagination pagination,
            TableContinuationToken continuationToken,
            string kindId,
            string teamId,
            string judgeId,
            RatingQueryOptions expectedOptions,
            string expectedLink)
        {
            // input
            var hackName = "Hack";
            HackathonEntity hackathonEntity = new HackathonEntity();
            var ratings = new List<RatingEntity>
            {
                new RatingEntity
                {
                    PartitionKey = "hack",
                    RowKey = "rk",
                    RatingKindId = "kid",
                    JudgeId = "judgeid",
                    TeamId = "tid",
                    Score = 4,
                }
            };
            RatingKindEntity ratingKindEntity = new RatingKindEntity { MaximumScore = 5 };
            TeamEntity team = new TeamEntity { CreatorId = "creator" };
            UserInfo judge = new UserInfo { OpenId = "openid" };
            UserInfo teamCreator = new UserInfo { Unionid = "unionid" };
            var segment = MockHelper.CreateTableQuerySegment(ratings, continuationToken);

            // moq
            RatingQueryOptions optionsCaptured = null;
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathonEntity);
            var ratingManagement = new Mock<IRatingManagement>();
            ratingManagement.Setup(r => r.GetCachedRatingKindAsync("hack", "kid", default)).ReturnsAsync(ratingKindEntity);
            ratingManagement.Setup(r => r.ListPaginatedRatingsAsync("hack", It.Is<RatingQueryOptions>(r =>
                    r.RatingKindId == expectedOptions.RatingKindId &&
                    r.TeamId == expectedOptions.TeamId &&
                    r.JudgeId == expectedOptions.JudgeId
                ), default))
                .Callback<string, RatingQueryOptions, CancellationToken>((h, r, c) =>
                {
                    optionsCaptured = r;
                })
                .ReturnsAsync(segment);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("hack", "tid", default)).ReturnsAsync(team);
            var userManagement = new Mock<IUserManagement>();
            userManagement.Setup(u => u.GetUserByIdAsync("judgeid", default)).ReturnsAsync(judge);
            userManagement.Setup(u => u.GetUserByIdAsync("creator", default)).ReturnsAsync(teamCreator);

            // run
            var controller = new RatingController
            {
                HackathonManagement = hackathonManagement.Object,
                RatingManagement = ratingManagement.Object,
                TeamManagement = teamManagement.Object,
                UserManagement = userManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
            };
            var result = await controller.ListPaginatedRatings(hackName, kindId, teamId, judgeId, pagination, default);

            // verify
            Mock.VerifyAll(hackathonManagement, ratingManagement, teamManagement, userManagement);
            hackathonManagement.VerifyNoOtherCalls();
            ratingManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            userManagement.VerifyNoOtherCalls();

            var list = AssertHelper.AssertOKResult<RatingList>(result);
            Assert.AreEqual(expectedLink, list.nextLink);
            Assert.AreEqual(1, list.value.Length);
            Assert.AreEqual("hack", list.value[0].hackathonName);
            Assert.AreEqual("rk", list.value[0].id);
            Assert.AreEqual(4, list.value[0].score);
            Assert.AreEqual("unionid", list.value[0].team.creator.Unionid);
            Assert.AreEqual("openid", list.value[0].judge.OpenId);
            Assert.AreEqual(5, list.value[0].ratingKind.maximumScore);
            Assert.AreEqual(expectedOptions.Top, optionsCaptured.Top);
            Assert.AreEqual(expectedOptions.TableContinuationToken?.NextPartitionKey, optionsCaptured.TableContinuationToken?.NextPartitionKey);
            Assert.AreEqual(expectedOptions.TableContinuationToken?.NextRowKey, optionsCaptured.TableContinuationToken?.NextRowKey);
        }

        #endregion

        #region GetRating
        [Test]
        public async Task GetRating()
        {
            // data
            HackathonEntity hackathon = new HackathonEntity { };
            RatingEntity ratingEntity = new RatingEntity
            {
                JudgeId = "anotherUser",
                Score = 4,
                RatingKindId = "kid",
                TeamId = "tid",
                PartitionKey = "hack"
            };
            RatingKindEntity ratingKindEntity = new RatingKindEntity { MaximumScore = 5 };
            TeamEntity team = new TeamEntity { CreatorId = "creator" };
            UserInfo judge = new UserInfo { OAuth = "oauth" };
            UserInfo teamCreator = new UserInfo { SignedUp = "signedup" };

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);
            var ratingManagement = new Mock<IRatingManagement>();
            ratingManagement.Setup(r => r.GetRatingAsync("hack", "rid", default)).ReturnsAsync(ratingEntity);
            ratingManagement.Setup(r => r.GetCachedRatingKindAsync("hack", "kid", default)).ReturnsAsync(ratingKindEntity);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("hack", "tid", default)).ReturnsAsync(team);
            var userManagement = new Mock<IUserManagement>();
            userManagement.Setup(u => u.GetUserByIdAsync("anotherUser", default)).ReturnsAsync(judge);
            userManagement.Setup(u => u.GetUserByIdAsync("creator", default)).ReturnsAsync(teamCreator);

            // test
            var controller = new RatingController
            {
                HackathonManagement = hackathonManagement.Object,
                RatingManagement = ratingManagement.Object,
                TeamManagement = teamManagement.Object,
                UserManagement = userManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
            };
            var result = await controller.GetRating("Hack", "rid", default);

            // verify
            Mock.VerifyAll(hackathonManagement, ratingManagement, teamManagement, userManagement);
            hackathonManagement.VerifyNoOtherCalls();
            ratingManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            userManagement.VerifyNoOtherCalls();

            var resp = AssertHelper.AssertOKResult<Rating>(result);
            Assert.AreEqual(4, resp.score);
            Assert.AreEqual("signedup", resp.team.creator.SignedUp);
            Assert.AreEqual("oauth", resp.judge.OAuth);
            Assert.AreEqual(5, resp.ratingKind.maximumScore);
        }
        #endregion

        #region DeleteRating
        [Test]
        public async Task DeleteRating_AlreadyDeleted()
        {
            HackathonEntity hackathon = new HackathonEntity { };
            var authResult = AuthorizationResult.Success();
            RatingEntity ratingEntity = null;

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), hackathon, AuthConstant.Policy.HackathonJudge))
               .ReturnsAsync(authResult);
            var ratingManagement = new Mock<IRatingManagement>();
            ratingManagement.Setup(r => r.GetRatingAsync("hack", "rid", default)).ReturnsAsync(ratingEntity);

            // test
            var controller = new RatingController
            {
                HackathonManagement = hackathonManagement.Object,
                AuthorizationService = authorizationService.Object,
                RatingManagement = ratingManagement.Object,
            };
            var result = await controller.DeleteRating("Hack", "rid", default);

            // verify
            Mock.VerifyAll(hackathonManagement, authorizationService, ratingManagement);
            hackathonManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();
            ratingManagement.VerifyNoOtherCalls();

            AssertHelper.AssertNoContentResult(result);
        }

        [Test]
        public async Task DeleteRating_NotCreator()
        {
            HackathonEntity hackathon = new HackathonEntity { };
            var authResult = AuthorizationResult.Success();
            RatingEntity ratingEntity = new RatingEntity { JudgeId = "user" };

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), hackathon, AuthConstant.Policy.HackathonJudge))
               .ReturnsAsync(authResult);
            var ratingManagement = new Mock<IRatingManagement>();
            ratingManagement.Setup(r => r.GetRatingAsync("hack", "rid", default)).ReturnsAsync(ratingEntity);
            var adminManagement = new Mock<IHackathonAdminManagement>();
            adminManagement.Setup(a => a.IsHackathonAdmin("hack", It.IsAny<ClaimsPrincipal>(), default)).ReturnsAsync(false);

            // test
            var controller = new RatingController
            {
                HackathonManagement = hackathonManagement.Object,
                AuthorizationService = authorizationService.Object,
                RatingManagement = ratingManagement.Object,
                HackathonAdminManagement = adminManagement.Object,
            };
            var result = await controller.DeleteRating("Hack", "rid", default);

            // verify
            Mock.VerifyAll(hackathonManagement, authorizationService, ratingManagement, adminManagement);
            hackathonManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();
            ratingManagement.VerifyNoOtherCalls();
            adminManagement.VerifyNoOtherCalls();

            AssertHelper.AssertObjectResult(result, 403, Resources.Rating_OnlyCreator);
        }

        [Test]
        public async Task DeleteRating_Delete()
        {
            HackathonEntity hackathon = new HackathonEntity { };
            var authResult = AuthorizationResult.Success();
            RatingEntity ratingEntity = new RatingEntity { JudgeId = "user" };

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), hackathon, AuthConstant.Policy.HackathonJudge))
               .ReturnsAsync(authResult);
            var ratingManagement = new Mock<IRatingManagement>();
            ratingManagement.Setup(r => r.GetRatingAsync("hack", "rid", default)).ReturnsAsync(ratingEntity);
            ratingManagement.Setup(r => r.DeleteRatingAsync("hack", "rid", default));
            var adminManagement = new Mock<IHackathonAdminManagement>();
            adminManagement.Setup(a => a.IsHackathonAdmin("hack", It.IsAny<ClaimsPrincipal>(), default)).ReturnsAsync(true);

            // test
            var controller = new RatingController
            {
                HackathonManagement = hackathonManagement.Object,
                AuthorizationService = authorizationService.Object,
                RatingManagement = ratingManagement.Object,
                HackathonAdminManagement = adminManagement.Object,
            };
            var result = await controller.DeleteRating("Hack", "rid", default);

            // verify
            Mock.VerifyAll(hackathonManagement, authorizationService, ratingManagement, adminManagement);
            hackathonManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();
            ratingManagement.VerifyNoOtherCalls();
            adminManagement.VerifyNoOtherCalls();

            AssertHelper.AssertNoContentResult(result);
        }
        #endregion
    }
}
