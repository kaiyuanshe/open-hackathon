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
        [TestCase("")]
        [TestCase("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")]
        [TestCase("@")]
        [TestCase("#")]
        [TestCase("%")]
        [TestCase("-")]
        [TestCase("_")]
        [TestCase("=")]
        [TestCase(" ")]
        public async Task CheckNameAvailability_Invalid(string name)
        {
            var parameter = new NameAvailability { name = name };
            CancellationToken cancellationToken = CancellationToken.None;

            var controller = new HackathonController();
            var result = await controller.CheckNameAvailability(parameter, cancellationToken);
            NameAvailability resp = (NameAvailability)(result);
            Assert.AreEqual(name, resp.name);
            Assert.IsFalse(resp.nameAvailable);
            Assert.AreEqual("Invalid", resp.reason);
            Assert.AreEqual(Resources.Hackathon_Name_Invalid, resp.message);
        }

        [Test]
        public async Task CheckNameAvailability_AlreadyExists()
        {
            var parameter = new NameAvailability { name = "Foo" };
            CancellationToken cancellationToken = CancellationToken.None;
            HackathonEntity entity = new HackathonEntity();

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(h => h.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(entity);

            var controller = new HackathonController
            {
                HackathonManagement = hackathonManagement.Object,
            };
            var result = await controller.CheckNameAvailability(parameter, cancellationToken);

            NameAvailability resp = (NameAvailability)(result);
            Assert.AreEqual("Foo", resp.name);
            Assert.IsFalse(resp.nameAvailable);
            Assert.AreEqual("AlreadyExists", resp.reason);
            Assert.AreEqual(Resources.Hackathon_Name_Taken, resp.message);
        }

        [Test]
        public async Task CheckNameAvailability_OK()
        {
            var parameter = new NameAvailability { name = "Foo" };
            CancellationToken cancellationToken = CancellationToken.None;
            HackathonEntity entity = null;

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(h => h.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(entity);

            var controller = new HackathonController
            {
                HackathonManagement = hackathonManagement.Object,
            };
            var result = await controller.CheckNameAvailability(parameter, cancellationToken);

            NameAvailability resp = (NameAvailability)(result);
            Assert.AreEqual("Foo", resp.name);
            Assert.IsTrue(resp.nameAvailable);
        }

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
            var role = new HackathonRoles { isAdmin = true };
            CancellationToken cancellationToken = CancellationToken.None;

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync(It.IsAny<string>(), cancellationToken))
                .ReturnsAsync(default(HackathonEntity));
            hackathonManagement.Setup(p => p.CreateHackathonAsync(hack, cancellationToken))
                .ReturnsAsync(inserted);
            hackathonManagement.Setup(h => h.GetHackathonRolesAsync("test1", null, cancellationToken))
                .ReturnsAsync(role);

            var controller = new HackathonController();
            controller.HackathonManagement = hackathonManagement.Object;
            controller.ResponseBuilder = new DefaultResponseBuilder();
            var result = await controller.CreateOrUpdate(name, hack, cancellationToken);

            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            Assert.AreEqual(name.ToLower(), hack.name);
            Assert.IsTrue(result is OkObjectResult);
            OkObjectResult objectResult = (OkObjectResult)result;
            Hackathon resp = (Hackathon)objectResult.Value;
            Assert.AreEqual("test2", resp.name);
            Assert.IsTrue(resp.autoApprove);
            Assert.IsTrue(resp.roles.isAdmin);
        }

        [Test]
        public async Task CreateOrUpdateTest_UpdateForbidden()
        {
            var hack = new Hackathon();
            var entity = new HackathonEntity();
            var name = "test1";
            var authResult = AuthorizationResult.Failed();
            CancellationToken cancellationToken = CancellationToken.None;

            var hackManagerMock = new Mock<IHackathonManagement>();
            hackManagerMock.Setup(p => p.GetHackathonEntityByNameAsync(It.IsAny<string>(), cancellationToken))
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
            var result = await controller.CreateOrUpdate(name, hack, cancellationToken);

            Mock.VerifyAll(hackManagerMock, authorizationServiceMock);
            hackManagerMock.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 403, Resources.Hackathon_NotAdmin);
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
            var role = new HackathonRoles { isAdmin = true };
            CancellationToken cancellationToken = CancellationToken.None;

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync(It.IsAny<string>(), cancellationToken))
                .ReturnsAsync(entity);
            hackathonManagement.Setup(p => p.UpdateHackathonAsync(hack, cancellationToken))
                .ReturnsAsync(entity);
            hackathonManagement.Setup(h => h.GetHackathonRolesAsync("test1", It.IsAny<ClaimsPrincipal>(), cancellationToken))
               .ReturnsAsync(role);
            var authorizationServiceMock = new Mock<IAuthorizationService>();
            authorizationServiceMock.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), entity, AuthConstant.Policy.HackathonAdministrator))
                .ReturnsAsync(authResult);

            var controller = new HackathonController();
            controller.HackathonManagement = hackathonManagement.Object;
            controller.AuthorizationService = authorizationServiceMock.Object;
            controller.ResponseBuilder = new DefaultResponseBuilder();
            var result = await controller.CreateOrUpdate(name, hack, cancellationToken);

            Mock.VerifyAll(hackathonManagement, authorizationServiceMock);
            hackathonManagement.VerifyNoOtherCalls();
            Assert.AreEqual(name, hack.name);
            Assert.IsTrue(result is OkObjectResult);
            OkObjectResult objectResult = (OkObjectResult)result;
            Assert.IsTrue(objectResult.Value is Hackathon);
            Hackathon resp = (Hackathon)objectResult.Value;
            Assert.AreEqual("test2", resp.name);
            Assert.IsTrue(resp.autoApprove);
            Assert.IsTrue(resp.roles.isAdmin);
        }

        [Test]
        public async Task UpdateTest_NotFound()
        {
            string name = "Foo";
            HackathonEntity entity = null;
            Hackathon parameter = new Hackathon();
            CancellationToken cancellationToken = CancellationToken.None;

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(m => m.GetHackathonEntityByNameAsync("foo", CancellationToken.None))
                .ReturnsAsync(entity);

            var controller = new HackathonController
            {
                HackathonManagement = hackathonManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.Update(name, parameter, cancellationToken);

            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 404, string.Format(Resources.Hackathon_NotFound, name.ToLower()));
        }

        [Test]
        public async Task UpdateTest_AccessDenied()
        {
            string name = "Foo";
            HackathonEntity entity = new HackathonEntity { };
            Hackathon parameter = new Hackathon();
            var authResult = AuthorizationResult.Failed();
            CancellationToken cancellationToken = CancellationToken.None;

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(m => m.GetHackathonEntityByNameAsync("foo", cancellationToken))
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
            var result = await controller.Update(name, parameter, cancellationToken);

            Mock.VerifyAll(hackathonManagement, authorizationServiceMock);
            hackathonManagement.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 403, Resources.Hackathon_NotAdmin);
        }

        [Test]
        public async Task UpdateTest_Updated()
        {
            string name = "Foo";
            HackathonEntity entity = new HackathonEntity { DisplayName = "displayname" };
            Hackathon parameter = new Hackathon();
            var authResult = AuthorizationResult.Success();
            CancellationToken cancellationToken = CancellationToken.None;
            var role = new HackathonRoles { isAdmin = true };

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(m => m.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(entity);
            hackathonManagement.Setup(p => p.UpdateHackathonAsync(parameter, cancellationToken))
                .ReturnsAsync(entity);
            hackathonManagement.Setup(h => h.GetHackathonRolesAsync("foo", It.IsAny<ClaimsPrincipal>(), cancellationToken))
               .ReturnsAsync(role);
            var authorizationServiceMock = new Mock<IAuthorizationService>();
            authorizationServiceMock.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), entity, AuthConstant.Policy.HackathonAdministrator))
                .ReturnsAsync(authResult);

            var controller = new HackathonController
            {
                HackathonManagement = hackathonManagement.Object,
                AuthorizationService = authorizationServiceMock.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
            };
            var result = await controller.Update(name, parameter, cancellationToken);

            Mock.VerifyAll(hackathonManagement, authorizationServiceMock);
            hackathonManagement.VerifyNoOtherCalls();
            Assert.AreEqual(name.ToLower(), parameter.name);
            Assert.IsTrue(result is OkObjectResult);
            OkObjectResult objectResult = (OkObjectResult)result;
            Assert.IsTrue(objectResult.Value is Hackathon);
            Hackathon resp = (Hackathon)objectResult.Value;
            Assert.AreEqual("displayname", resp.displayName);
            Assert.IsTrue(resp.roles.isAdmin);
        }

        [Test]
        public async Task GetTest_NotFound()
        {
            string name = "Foo";
            HackathonEntity entity = null;
            CancellationToken cancellationToken = CancellationToken.None;

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(m => m.GetHackathonEntityByNameAsync("foo", CancellationToken.None))
                .ReturnsAsync(entity);

            var controller = new HackathonController
            {
                HackathonManagement = hackathonManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.Get(name, cancellationToken);

            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 404, string.Format(Resources.Hackathon_NotFound, name));
        }

        [Test]
        public async Task GetTest_NotOnlineAnonymous()
        {
            string name = "Foo";
            HackathonEntity entity = new HackathonEntity { Detail = "detail" };
            CancellationToken cancellationToken = CancellationToken.None;
            HackathonRoles role = null;

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(m => m.GetHackathonEntityByNameAsync("foo", CancellationToken.None))
                .ReturnsAsync(entity);
            hackathonManagement.Setup(h => h.GetHackathonRolesAsync("foo", It.IsAny<ClaimsPrincipal>(), cancellationToken))
              .ReturnsAsync(role);

            var controller = new HackathonController
            {
                HackathonManagement = hackathonManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.Get(name, cancellationToken);

            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 404, string.Format(Resources.Hackathon_NotFound, name));
        }

        [Test]
        public async Task GetTest_NotOnlineNotAdmin()
        {
            string name = "Foo";
            HackathonEntity entity = new HackathonEntity { Detail = "detail" };
            CancellationToken cancellationToken = CancellationToken.None;
            HackathonRoles role = new HackathonRoles { isAdmin = false };

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(m => m.GetHackathonEntityByNameAsync("foo", CancellationToken.None))
                .ReturnsAsync(entity);
            hackathonManagement.Setup(h => h.GetHackathonRolesAsync("foo", It.IsAny<ClaimsPrincipal>(), cancellationToken))
              .ReturnsAsync(role);

            var controller = new HackathonController
            {
                HackathonManagement = hackathonManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.Get(name, cancellationToken);

            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 404, string.Format(Resources.Hackathon_NotFound, name));
        }

        [Test]
        public async Task GetTest_OK()
        {
            string name = "Foo";
            HackathonEntity entity = new HackathonEntity { Detail = "detail" };
            CancellationToken cancellationToken = CancellationToken.None;
            var role = new HackathonRoles { isAdmin = true };

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(m => m.GetHackathonEntityByNameAsync("foo", CancellationToken.None))
                .ReturnsAsync(entity);
            hackathonManagement.Setup(h => h.GetHackathonRolesAsync("foo", It.IsAny<ClaimsPrincipal>(), cancellationToken))
              .ReturnsAsync(role);

            var controller = new HackathonController
            {
                HackathonManagement = hackathonManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
            };
            var result = await controller.Get(name, cancellationToken);

            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            Assert.IsTrue(result is OkObjectResult);
            Hackathon hackathon = ((OkObjectResult)result).Value as Hackathon;
            Assert.IsNotNull(hackathon);
            Assert.AreEqual("detail", hackathon.detail);
            Assert.IsTrue(hackathon.roles.isAdmin);
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
