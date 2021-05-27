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
using System;
using System.Collections.Generic;
using System.Security.Claims;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Controllers
{
    public class AwardControllerTests
    {
        #region CreateAward
        [Test]
        public async Task CreateAward()
        {
            // input
            string hackName = "Foo";
            HackathonEntity hackathon = new HackathonEntity { };
            Award parameter = new Award { };
            AwardEntity awardEntity = new AwardEntity
            {
                Name = "n",
                PartitionKey = "pk",
                RowKey = "rk",
                Description = "desc",
                Quantity = 5,
                Target = AwardTarget.individual,
                Pictures = new PictureInfo[]
                {
                    new PictureInfo{ Name="p1", Description="d1", Uri="u1" },
                }
            };
            CancellationToken cancellationToken = CancellationToken.None;
            var authResult = AuthorizationResult.Success();

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(hackathon);
            var awardManagement = new Mock<IAwardManagement>();
            awardManagement.Setup(t => t.CreateAwardAsync("foo", parameter, cancellationToken))
                .ReturnsAsync(awardEntity);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), hackathon, AuthConstant.Policy.HackathonAdministrator))
                .ReturnsAsync(authResult);

            // run
            var controller = new AwardController
            {
                HackathonManagement = hackathonManagement.Object,
                AwardManagement = awardManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
                ResponseBuilder = new DefaultResponseBuilder(),
                AuthorizationService = authorizationService.Object,
            };
            var result = await controller.CreateAward(hackName, parameter, cancellationToken);

            // verify
            Mock.VerifyAll(hackathonManagement, awardManagement, authorizationService);
            hackathonManagement.VerifyNoOtherCalls();
            awardManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();

            Award resp = AssertHelper.AssertOKResult<Award>(result);
            Assert.AreEqual("desc", resp.description);
            Assert.AreEqual("pk", resp.hackathonName);
            Assert.AreEqual("rk", resp.id);
            Assert.AreEqual("n", resp.name);
            Assert.AreEqual(5, resp.quantity);
            Assert.AreEqual(AwardTarget.individual, resp.target);
            Assert.AreEqual(1, resp.pictures.Length);
            Assert.AreEqual("d1", resp.pictures[0].Description);
            Assert.AreEqual("u1", resp.pictures[0].Uri);
            Assert.AreEqual("p1", resp.pictures[0].Name);
        }
        #endregion

        #region GetAward
        [Test]
        public async Task GetAward_AwardNotFound()
        {
            // input
            string hackName = "Foo";
            HackathonEntity hackathon = new HackathonEntity { };
            string awardId = "aid";
            AwardEntity awardEntity = null;
            CancellationToken cancellationToken = CancellationToken.None;

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(hackathon);
            var awardManagement = new Mock<IAwardManagement>();
            awardManagement.Setup(t => t.GetAwardByIdAsync("foo", awardId, cancellationToken))
                .ReturnsAsync(awardEntity);

            // run
            var controller = new AwardController
            {
                HackathonManagement = hackathonManagement.Object,
                AwardManagement = awardManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.GetAward(hackName, awardId, cancellationToken);

            // verify
            Mock.VerifyAll(hackathonManagement, awardManagement);
            hackathonManagement.VerifyNoOtherCalls();
            awardManagement.VerifyNoOtherCalls();

            AssertHelper.AssertObjectResult(result, 404, Resources.Award_NotFound);
        }

        [Test]
        public async Task GetAward_Succeeded()
        {
            // input
            string hackName = "Foo";
            HackathonEntity hackathon = new HackathonEntity { };
            string awardId = "aid";
            AwardEntity awardEntity = new AwardEntity
            {
                Name = "n",
                PartitionKey = "pk",
                RowKey = "rk",
                Description = "desc",
                Quantity = 5,
                Target = AwardTarget.individual,
                Pictures = new PictureInfo[]
                {
                    new PictureInfo{ Name="p1", Description="d1", Uri="u1" },
                }
            };
            CancellationToken cancellationToken = CancellationToken.None;

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(hackathon);
            var awardManagement = new Mock<IAwardManagement>();
            awardManagement.Setup(t => t.GetAwardByIdAsync("foo", awardId, cancellationToken))
                .ReturnsAsync(awardEntity);

            // run
            var controller = new AwardController
            {
                HackathonManagement = hackathonManagement.Object,
                AwardManagement = awardManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
                ResponseBuilder = new DefaultResponseBuilder(),
            };
            var result = await controller.GetAward(hackName, awardId, cancellationToken);

            // verify
            Mock.VerifyAll(hackathonManagement, awardManagement);
            hackathonManagement.VerifyNoOtherCalls();
            awardManagement.VerifyNoOtherCalls();

            Award resp = AssertHelper.AssertOKResult<Award>(result);
            Assert.AreEqual("desc", resp.description);
            Assert.AreEqual("pk", resp.hackathonName);
            Assert.AreEqual("rk", resp.id);
            Assert.AreEqual("n", resp.name);
            Assert.AreEqual(5, resp.quantity);
            Assert.AreEqual(AwardTarget.individual, resp.target);
            Assert.AreEqual(1, resp.pictures.Length);
            Assert.AreEqual("d1", resp.pictures[0].Description);
            Assert.AreEqual("u1", resp.pictures[0].Uri);
            Assert.AreEqual("p1", resp.pictures[0].Name);
        }
        #endregion

        #region UpdateAward
        [Test]
        public async Task UpdateAward()
        {
            // input
            string hackName = "Foo";
            string awardId = "aid";
            HackathonEntity hackathon = new HackathonEntity { };
            Award parameter = new Award { };
            AwardEntity awardEntity = new AwardEntity
            {
                Name = "n",
                PartitionKey = "pk",
                RowKey = "rk",
                Description = "desc",
                Quantity = 5,
                Target = AwardTarget.individual,
                Pictures = new PictureInfo[]
                {
                    new PictureInfo{ Name="p1", Description="d1", Uri="u1" },
                }
            };
            CancellationToken cancellationToken = CancellationToken.None;
            var authResult = AuthorizationResult.Success();

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(hackathon);
            var awardManagement = new Mock<IAwardManagement>();
            awardManagement.Setup(t => t.GetAwardByIdAsync("foo", awardId, cancellationToken))
                .ReturnsAsync(awardEntity);
            awardManagement.Setup(t => t.UpdateAwardAsync(awardEntity, parameter, cancellationToken))
                .ReturnsAsync(awardEntity);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), hackathon, AuthConstant.Policy.HackathonAdministrator))
                .ReturnsAsync(authResult);

            // run
            var controller = new AwardController
            {
                HackathonManagement = hackathonManagement.Object,
                AwardManagement = awardManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
                ResponseBuilder = new DefaultResponseBuilder(),
                AuthorizationService = authorizationService.Object,
            };
            var result = await controller.UpdateAward(hackName, awardId, parameter, cancellationToken);

            // verify
            Mock.VerifyAll(hackathonManagement, awardManagement, authorizationService);
            hackathonManagement.VerifyNoOtherCalls();
            awardManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();

            Award resp = AssertHelper.AssertOKResult<Award>(result);
            Assert.AreEqual("desc", resp.description);
            Assert.AreEqual("pk", resp.hackathonName);
            Assert.AreEqual("rk", resp.id);
            Assert.AreEqual("n", resp.name);
            Assert.AreEqual(5, resp.quantity);
            Assert.AreEqual(AwardTarget.individual, resp.target);
            Assert.AreEqual(1, resp.pictures.Length);
            Assert.AreEqual("d1", resp.pictures[0].Description);
            Assert.AreEqual("u1", resp.pictures[0].Uri);
            Assert.AreEqual("p1", resp.pictures[0].Name);
        }
        #endregion
    }
}
