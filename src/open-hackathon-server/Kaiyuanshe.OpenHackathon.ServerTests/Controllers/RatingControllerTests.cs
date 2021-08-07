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
            RatingKindEntity awardEntity = new RatingKindEntity
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
            ratingManagement.Setup(t => t.CreateRatingKindAsync(parameter, default)).ReturnsAsync(awardEntity);

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
    }
}
