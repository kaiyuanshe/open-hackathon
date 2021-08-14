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
            RatingKindEntity entity = firstTime ? new RatingKindEntity() : null;

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), hackathon, AuthConstant.Policy.HackathonAdministrator)).ReturnsAsync(authResult);
            var ratingManagement = new Mock<IRatingManagement>();
            ratingManagement.Setup(j => j.GetRatingKindAsync("hack", "kid", default)).ReturnsAsync(entity);
            if (firstTime)
            {
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
        #endregion
    }
}
