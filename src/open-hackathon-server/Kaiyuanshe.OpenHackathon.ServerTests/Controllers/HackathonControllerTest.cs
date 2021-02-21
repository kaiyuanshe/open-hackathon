using Kaiyuanshe.OpenHackathon.Server;
using Kaiyuanshe.OpenHackathon.Server.Auth;
using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Controllers;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.ResponseBuilder;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Moq;
using NUnit.Framework;
using System.Security.Claims;
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

            var controller = new HackathonController
            {
                HackathonManagement = hackManagerMock.Object,
                AuthorizationService = authorizationServiceMock.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.CreateOrUpdate(name, hack);

            Mock.VerifyAll(hackManagerMock, authorizationServiceMock);
            hackManagerMock.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 403, Resources.Request_Forbidden_HackAdmin);
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
        public async Task UpdateTest_NotFound()
        {
            string name = "Foo";
            HackathonEntity entity = null;
            Hackathon parameter = new Hackathon();

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(m => m.GetHackathonEntityByNameAsync("foo", CancellationToken.None))
                .ReturnsAsync(entity);

            var controller = new HackathonController
            {
                HackathonManagement = hackathonManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.Update(name, parameter);

            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 404, string.Format(Resources.Hackathon_NotFound, name));
        }

        [Test]
        public async Task UpdateTest_AccessDenied()
        {
            string name = "Foo";
            HackathonEntity entity = new HackathonEntity { };
            Hackathon parameter = new Hackathon();
            var authResult = AuthorizationResult.Failed();

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(m => m.GetHackathonEntityByNameAsync("foo", CancellationToken.None))
                .ReturnsAsync(entity);
            var authorizationServiceMock = new Mock<IAuthorizationService>();
            authorizationServiceMock.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), entity, AuthConstant.Policy.HackathonAdministrator))
                .ReturnsAsync(authResult);

            var controller = new HackathonController
            {
                HackathonManagement = hackathonManagement.Object,
                AuthorizationService = authorizationServiceMock.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.Update(name, parameter);

            Mock.VerifyAll(hackathonManagement, authorizationServiceMock);
            hackathonManagement.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 403, Resources.Request_Forbidden_HackAdmin);
        }

        [Test]
        public async Task UpdateTest_Updated()
        {
            string name = "Foo";
            HackathonEntity entity = new HackathonEntity { DisplayName = "displayname" };
            Hackathon parameter = new Hackathon();
            var authResult = AuthorizationResult.Success();

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(m => m.GetHackathonEntityByNameAsync("foo", CancellationToken.None))
                .ReturnsAsync(entity);
            hackathonManagement.Setup(p => p.UpdateHackathonAsync(parameter, It.IsAny<CancellationToken>()))
                .ReturnsAsync(entity);
            var authorizationServiceMock = new Mock<IAuthorizationService>();
            authorizationServiceMock.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), entity, AuthConstant.Policy.HackathonAdministrator))
                .ReturnsAsync(authResult);

            var controller = new HackathonController
            {
                HackathonManagement = hackathonManagement.Object,
                AuthorizationService = authorizationServiceMock.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
            };
            var result = await controller.Update(name, parameter);

            Mock.VerifyAll(hackathonManagement, authorizationServiceMock);
            hackathonManagement.VerifyNoOtherCalls();
            Assert.AreEqual(name.ToLower(), parameter.Name);
            Assert.IsTrue(result is OkObjectResult);
            OkObjectResult objectResult = (OkObjectResult)result;
            Assert.IsTrue(objectResult.Value is Hackathon);
            Hackathon resp = (Hackathon)objectResult.Value;
            Assert.AreEqual("displayname", resp.DisplayName);
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
                HackathonManagement = hackathonManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.Get(name);

            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 404, string.Format(Resources.Hackathon_NotFound, name));
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

        [Test]
        public async Task DeleteTest_NotExist()
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
            var result = await controller.Delete(name);

            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            Assert.IsTrue(result is NoContentResult);
        }

        [Test]
        public async Task DeleteTest_AlreadyDeleted()
        {
            string name = "Foo";
            HackathonEntity entity = new HackathonEntity { IsDeleted = true };

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(m => m.GetHackathonEntityByNameAsync("foo", CancellationToken.None))
                .ReturnsAsync(entity);

            var controller = new HackathonController
            {
                HackathonManagement = hackathonManagement.Object
            };
            var result = await controller.Delete(name);

            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            Assert.IsTrue(result is NoContentResult);
        }

        [Test]
        public async Task DeleteTest_DeleteLogically()
        {
            string name = "Foo";
            HackathonEntity entity = new HackathonEntity();

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(m => m.GetHackathonEntityByNameAsync("foo", CancellationToken.None))
                .ReturnsAsync(entity);
            hackathonManagement.Setup(m => m.DeleteHackathonLogically("foo", CancellationToken.None));

            var controller = new HackathonController
            {
                HackathonManagement = hackathonManagement.Object
            };
            var result = await controller.Delete(name);

            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            Assert.IsTrue(result is NoContentResult);
        }
    }
}
