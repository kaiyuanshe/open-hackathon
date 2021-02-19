using Kaiyuanshe.OpenHackathon.Server;
using Kaiyuanshe.OpenHackathon.Server.Auth;
using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Controllers;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.ResponseBuilder;
using Kaiyuanshe.OpenHackathon.Server.Storage;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
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
    [TestFixture]
    public class HackathonControllerTest
    {
        [Test]
        public async Task CreateOrUpdateTest_Create()
        {
            var hack = new Hackathon();
            var name = "Test1";
            var inserted = new HackathonEntity
            {
                PartitionKey = "test2",
                AutoApprove = true
            };

            var hackManagerMock = new Mock<IHackathonManagement>();
            hackManagerMock.Setup(p => p.GetHackathonEntityByNameAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
                .ReturnsAsync(default(HackathonEntity));
            hackManagerMock.Setup(p => p.CreateHackathonAsync(hack, It.IsAny<CancellationToken>()))
                .ReturnsAsync(inserted);

            var controller = new HackathonController();
            controller.HackathonManagement = hackManagerMock.Object;
            controller.ResponseBuilder = new DefaultResponseBuilder();
            var result = await controller.CreateOrUpdate(name, hack);

            Mock.VerifyAll(hackManagerMock);
            hackManagerMock.VerifyNoOtherCalls();
            Assert.AreEqual(name.ToLower(), hack.Name);
            Assert.IsTrue(result is OkObjectResult);
            OkObjectResult objectResult = (OkObjectResult)result;
            Hackathon resp = (Hackathon)objectResult.Value;
            Assert.AreEqual("test2", resp.Name);
            Assert.IsTrue(resp.AutoApprove);
        }

        [Test]
        public async Task CreateOrUpdateTest_UpdateForbidden()
        {
            var hack = new Hackathon();
            var entity = new HackathonEntity();
            var name = "test1";
            var authResult = AuthorizationResult.Failed();

            var hackManagerMock = new Mock<IHackathonManagement>();
            hackManagerMock.Setup(p => p.GetHackathonEntityByNameAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
                .ReturnsAsync(entity);
            var authorizationServiceMock = new Mock<IAuthorizationService>();
            authorizationServiceMock.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), entity, AuthConstant.Policy.HackathonAdministrator))
                .ReturnsAsync(authResult);

            var controller = new HackathonController();
            controller.HackathonManagement = hackManagerMock.Object;
            controller.AuthorizationService = authorizationServiceMock.Object;
            var result = await controller.CreateOrUpdate(name, hack);

            Mock.VerifyAll(hackManagerMock, authorizationServiceMock);
            hackManagerMock.VerifyNoOtherCalls();
            Assert.AreEqual(name, hack.Name);
            Assert.IsTrue(result is ObjectResult);
            ObjectResult objectResult = (ObjectResult)result;
            Assert.AreEqual(403, objectResult.StatusCode);
            Assert.IsTrue(objectResult.Value is ErrorResponse);
            Assert.AreEqual("Forbidden", ((ErrorResponse)objectResult.Value).error.code);
        }

        [Test]
        public async Task CreateOrUpdateTest_UpdateSucceeded()
        {
            var hack = new Hackathon();
            var entity = new HackathonEntity
            {
                PartitionKey = "test2",
                AutoApprove = true
            };
            var name = "test1";
            var authResult = AuthorizationResult.Success();

            var hackManagerMock = new Mock<IHackathonManagement>();
            hackManagerMock.Setup(p => p.GetHackathonEntityByNameAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
                .ReturnsAsync(entity);
            hackManagerMock.Setup(p => p.UpdateHackathonAsync(hack, It.IsAny<CancellationToken>()))
                .ReturnsAsync(entity);
            var authorizationServiceMock = new Mock<IAuthorizationService>();
            authorizationServiceMock.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), entity, AuthConstant.Policy.HackathonAdministrator))
                .ReturnsAsync(authResult);

            var controller = new HackathonController();
            controller.HackathonManagement = hackManagerMock.Object;
            controller.AuthorizationService = authorizationServiceMock.Object;
            controller.ResponseBuilder = new DefaultResponseBuilder();
            var result = await controller.CreateOrUpdate(name, hack);

            Mock.VerifyAll(hackManagerMock, authorizationServiceMock);
            hackManagerMock.VerifyNoOtherCalls();
            Assert.AreEqual(name, hack.Name);
            Assert.IsTrue(result is OkObjectResult);
            OkObjectResult objectResult = (OkObjectResult)result;
            Assert.IsTrue(objectResult.Value is Hackathon);
            Hackathon resp = (Hackathon)objectResult.Value;
            Assert.AreEqual("test2", resp.Name);
            Assert.IsTrue(resp.AutoApprove);
        }

        [Test]
        public async Task GetTest_NotFound()
        {
            string name = "Foo";
            HackathonEntity entity = null;

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(m => m.GetHackathonEntityByNameAsync("foo", CancellationToken.None))
                .ReturnsAsync(entity);

            var controller = new HackathonController
            {
                HackathonManagement = hackathonManagement.Object
            };
            var result = await controller.Get(name);

            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            Assert.IsTrue(result is NotFoundObjectResult);
            ErrorResponse error = ((NotFoundObjectResult)result).Value as ErrorResponse;
            Assert.IsNotNull(error);
            Assert.AreEqual("NotFound", error.error.code);
            Assert.AreEqual(string.Format(Resources.Hackathon_NotFound, name), error.error.message);
        }

        [Test]
        public async Task GetTest_OK()
        {
            string name = "Foo";
            HackathonEntity entity = new HackathonEntity { Detail = "detail" };

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(m => m.GetHackathonEntityByNameAsync("foo", CancellationToken.None))
                .ReturnsAsync(entity);

            var controller = new HackathonController
            {
                HackathonManagement = hackathonManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
            };
            var result = await controller.Get(name);

            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            Assert.IsTrue(result is OkObjectResult);
            Hackathon hackathon = ((OkObjectResult)result).Value as Hackathon;
            Assert.IsNotNull(hackathon);
            Assert.AreEqual("detail", hackathon.Detail);
        }
    }
}
