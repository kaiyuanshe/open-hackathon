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
                MaximumRating = 5,
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
            Assert.AreEqual(5, resp.maximumRating);
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
    }
}
