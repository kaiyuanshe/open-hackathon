using Kaiyuanshe.OpenHackathon.Server;
using Kaiyuanshe.OpenHackathon.Server.Auth;
using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Controllers;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.ResponseBuilder;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.WindowsAzure.Storage.Table;
using Moq;
using NUnit.Framework;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Security.Claims;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Controllers
{
    [TestFixture]
    public class HackathonControllerTests
    {
        #region CheckNameAvailability
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

        #endregion

        #region CreateOrUpdate
        [Test]
        public async Task CreateOrUpdateTest_CreateTooMany()
        {
            var hack = new Hackathon();

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(default(HackathonEntity));
            hackathonManagement.Setup(p => p.CanCreateHackathonAsync(It.IsAny<ClaimsPrincipal>(), default)).ReturnsAsync(false);

            var controller = new HackathonController
            {
                HackathonManagement = hackathonManagement.Object,
            };
            var result = await controller.CreateOrUpdate("Hack", hack, default);

            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();

            AssertHelper.AssertObjectResult(result, 412, Resources.Hackathon_CreateTooMany);
        }

        [Test]
        public async Task CreateOrUpdateTest_Create()
        {
            var hack = new Hackathon();
            var inserted = new HackathonEntity
            {
                PartitionKey = "test2",
                AutoApprove = true
            };
            var role = new HackathonRoles { isAdmin = true };

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(default(HackathonEntity));
            hackathonManagement.Setup(p => p.CreateHackathonAsync(hack, default)).ReturnsAsync(inserted);
            hackathonManagement.Setup(h => h.GetHackathonRolesAsync(inserted, null, default)).ReturnsAsync(role);
            hackathonManagement.Setup(p => p.CanCreateHackathonAsync(It.IsAny<ClaimsPrincipal>(), default)).ReturnsAsync(true);

            var controller = new HackathonController();
            controller.HackathonManagement = hackathonManagement.Object;
            controller.ResponseBuilder = new DefaultResponseBuilder();
            var result = await controller.CreateOrUpdate("Hack", hack, default);

            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            Assert.AreEqual("hack", hack.name);

            Hackathon resp = AssertHelper.AssertOKResult<Hackathon>(result);
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
            hackathonManagement.Setup(h => h.GetHackathonRolesAsync(entity, It.IsAny<ClaimsPrincipal>(), cancellationToken))
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

        #endregion

        #region Update
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
        public async Task UpdateTest_ReadOnly()
        {
            string name = "Foo";
            HackathonEntity entity = new HackathonEntity { ReadOnly = true };
            Hackathon parameter = new Hackathon();

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(m => m.GetHackathonEntityByNameAsync("foo", default))
                .ReturnsAsync(entity);

            var controller = new HackathonController
            {
                HackathonManagement = hackathonManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.Update(name, parameter, default);

            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 403, Resources.Hackathon_ReadOnly);
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
            hackathonManagement.Setup(h => h.GetHackathonRolesAsync(entity, It.IsAny<ClaimsPrincipal>(), cancellationToken))
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

        #endregion

        #region Get
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
            hackathonManagement.Setup(h => h.GetHackathonRolesAsync(entity, It.IsAny<ClaimsPrincipal>(), cancellationToken))
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
            hackathonManagement.Setup(h => h.GetHackathonRolesAsync(entity, It.IsAny<ClaimsPrincipal>(), cancellationToken))
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
            HackathonEntity entity = new HackathonEntity { Detail = "detail", ReadOnly = true };
            CancellationToken cancellationToken = CancellationToken.None;
            var role = new HackathonRoles { isAdmin = true };

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(m => m.GetHackathonEntityByNameAsync("foo", CancellationToken.None))
                .ReturnsAsync(entity);
            hackathonManagement.Setup(h => h.GetHackathonRolesAsync(entity, It.IsAny<ClaimsPrincipal>(), cancellationToken))
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

        #endregion

        #region ListHackathon
        [Test]
        public async Task ListHackathon_Unauthorized()
        {
            // input
            var authResult = AuthorizationResult.Failed();

            // mock and capture
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), null, AuthConstant.PolicyForSwagger.LoginUser))
                .ReturnsAsync(authResult);

            // run
            var controller = new HackathonController
            {
                AuthorizationService = authorizationService.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.ListHackathon(null, null, null, HackathonListType.admin, default);

            // verify
            Mock.VerifyAll(authorizationService);
            authorizationService.VerifyNoOtherCalls();

            AssertHelper.AssertObjectResult(result, 401, Resources.Auth_Unauthorized);
        }

        private static IEnumerable ListHackathonTestData()
        {
            // arg0: pagination
            // arg1: search
            // arg2: order by
            // arg3: listType
            // arg4: next token
            // arg5: expected nextlink

            // no pagination, no filter, no top
            yield return new TestCaseData(
                    new Pagination { },
                    null,
                    null,
                    null,
                    null,
                    null
                );

            // with pagination and filters
            yield return new TestCaseData(
                    new Pagination { top = 10, np = "np", nr = "nr" },
                    "search",
                    HackathonOrderBy.updatedAt,
                    HackathonListType.online,
                    null,
                    null
                );

            // with pagination and filters
            yield return new TestCaseData(
                    new Pagination { top = 10 },
                    "search",
                    HackathonOrderBy.updatedAt,
                    HackathonListType.admin,
                    new TableContinuationToken { NextPartitionKey = "np", NextRowKey = "nr" },
                    "&top=10&search=search&orderby=updatedAt&listType=admin&np=np&nr=nr"
                );
            yield return new TestCaseData(
                    new Pagination { top = 10 },
                    "search",
                    HackathonOrderBy.updatedAt,
                    HackathonListType.online,
                    new TableContinuationToken { NextPartitionKey = "np", NextRowKey = "nr" },
                    "&top=10&search=search&orderby=updatedAt&listType=online&np=np&nr=nr"
                );
        }

        [Test, TestCaseSource(nameof(ListHackathonTestData))]
        public async Task ListHackathon(
            Pagination pagination,
            string search,
            HackathonOrderBy? orderBy,
            HackathonListType? listType,
            TableContinuationToken next,
            string expectedLink)
        {
            // input
            var hackathons = new List<HackathonEntity>
            {
                new HackathonEntity
                {
                    PartitionKey = "pk",
                    RowKey = "rk",
                }
            };
            var hackWithRoles = new List<Tuple<HackathonEntity, HackathonRoles>>()
            {
                Tuple.Create(hackathons.First(), new HackathonRoles{})
            };
            ClaimsPrincipal user = null;
            var authResult = AuthorizationResult.Success();

            // mock and capture
            var hackathonManagement = new Mock<IHackathonManagement>();
            HackathonQueryOptions optionsCaptured = null;
            hackathonManagement.Setup(p => p.ListPaginatedHackathonsAsync(user, It.IsAny<HackathonQueryOptions>(), default))
                .Callback<ClaimsPrincipal, HackathonQueryOptions, CancellationToken>((u, o, t) =>
                 {
                     optionsCaptured = o;
                     optionsCaptured.Next = next;
                 })
                .ReturnsAsync(hackathons);
            hackathonManagement.Setup(h => h.ListHackathonRolesAsync(hackathons, user, default))
                .ReturnsAsync(hackWithRoles);

            var authorizationService = new Mock<IAuthorizationService>();
            if (listType == HackathonListType.admin)
            {
                authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), null, AuthConstant.PolicyForSwagger.LoginUser))
                    .ReturnsAsync(authResult);
            }

            // run
            var controller = new HackathonController
            {
                ResponseBuilder = new DefaultResponseBuilder(),
                AuthorizationService = authorizationService.Object,
                HackathonManagement = hackathonManagement.Object,
            };
            var result = await controller.ListHackathon(pagination, search, orderBy, listType, default);

            // verify
            Mock.VerifyAll(hackathonManagement, authorizationService);
            hackathonManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();

            var list = AssertHelper.AssertOKResult<HackathonList>(result);
            Assert.AreEqual(expectedLink, list.nextLink);
            Assert.AreEqual(1, list.value.Length);
            Assert.AreEqual("pk", list.value[0].name);
            Assert.AreEqual(pagination.top, optionsCaptured.Top);
            Assert.AreEqual(orderBy, optionsCaptured.OrderBy);
            Assert.AreEqual(listType, optionsCaptured.ListType);
            Assert.AreEqual(pagination.np, optionsCaptured.TableContinuationToken?.NextPartitionKey);
            Assert.AreEqual(pagination.nr, optionsCaptured.TableContinuationToken?.NextRowKey);
        }
        #endregion

        #region Delete
        [Test]
        public async Task DeleteTest_NotExist()
        {
            string name = "Foo";
            HackathonEntity entity = null;
            CancellationToken cancellationToken = CancellationToken.None;

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(m => m.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(entity);

            var controller = new HackathonController
            {
                HackathonManagement = hackathonManagement.Object
            };
            var result = await controller.Delete(name, cancellationToken);

            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            AssertHelper.AssertNoContentResult(result);
        }

        [Test]
        public async Task DeleteTest_AlreadyDeleted()
        {
            string name = "Foo";
            HackathonEntity entity = new HackathonEntity { Status = HackathonStatus.offline };
            CancellationToken cancellationToken = CancellationToken.None;

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(m => m.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(entity);

            var controller = new HackathonController
            {
                HackathonManagement = hackathonManagement.Object
            };
            var result = await controller.Delete(name, cancellationToken);

            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            AssertHelper.AssertNoContentResult(result);
        }

        [Test]
        public async Task DeleteTest_DeleteLogically()
        {
            string name = "Foo";
            HackathonEntity entity = new HackathonEntity();
            CancellationToken cancellationToken = CancellationToken.None;

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(m => m.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(entity);
            hackathonManagement.Setup(m => m.UpdateHackathonStatusAsync(entity, HackathonStatus.offline, cancellationToken));

            var controller = new HackathonController
            {
                HackathonManagement = hackathonManagement.Object
            };
            var result = await controller.Delete(name, cancellationToken);

            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            AssertHelper.AssertNoContentResult(result);
        }

        #endregion

        #region RequestPublish
        [Test]
        public async Task RequestPublish_Deleted()
        {
            string name = "Foo";
            HackathonEntity entity = new HackathonEntity { Status = HackathonStatus.offline };
            CancellationToken cancellationToken = CancellationToken.None;

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(m => m.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(entity);

            var controller = new HackathonController
            {
                HackathonManagement = hackathonManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.RequestPublish(name, cancellationToken);

            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();

            AssertHelper.AssertObjectResult(result, 412, string.Format(Resources.Hackathon_Deleted, name));
        }

        [Test]
        public async Task RequestPublish_AlreadyOnline()
        {
            string name = "Foo";
            HackathonEntity entity = new HackathonEntity { Status = HackathonStatus.online };
            var authResult = AuthorizationResult.Success();
            CancellationToken cancellationToken = CancellationToken.None;

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(m => m.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(entity);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), entity, AuthConstant.Policy.HackathonAdministrator))
                .ReturnsAsync(authResult);

            var controller = new HackathonController
            {
                HackathonManagement = hackathonManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
                AuthorizationService = authorizationService.Object,
            };
            var result = await controller.RequestPublish(name, cancellationToken);

            Mock.VerifyAll(hackathonManagement, authorizationService);
            hackathonManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();

            AssertHelper.AssertObjectResult(result, 412, string.Format(Resources.Hackathon_AlreadyOnline, name));
        }

        [TestCase(HackathonStatus.planning)]
        [TestCase(HackathonStatus.pendingApproval)]
        public async Task RequestPublish_Succeeded(HackathonStatus status)
        {
            string name = "Foo";
            HackathonEntity entity = new HackathonEntity { Status = status };
            var authResult = AuthorizationResult.Success();
            var role = new HackathonRoles { isAdmin = true };
            CancellationToken cancellationToken = CancellationToken.None;

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(m => m.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(entity);
            hackathonManagement.Setup(m => m.UpdateHackathonStatusAsync(entity, HackathonStatus.pendingApproval, cancellationToken))
                .Callback<HackathonEntity, HackathonStatus, CancellationToken>((e, s, c) =>
                {
                    e.Status = s;
                })
                .ReturnsAsync(entity);
            hackathonManagement.Setup(h => h.GetHackathonRolesAsync(entity, null, cancellationToken))
               .ReturnsAsync(role);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), entity, AuthConstant.Policy.HackathonAdministrator))
                .ReturnsAsync(authResult);

            var controller = new HackathonController
            {
                HackathonManagement = hackathonManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
                AuthorizationService = authorizationService.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
            };
            var result = await controller.RequestPublish(name, cancellationToken);

            Mock.VerifyAll(hackathonManagement, authorizationService);
            hackathonManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();

            var resp = AssertHelper.AssertOKResult<Hackathon>(result);
            Assert.AreEqual(HackathonStatus.pendingApproval, resp.status);
        }
        #endregion

        #region Publish
        [TestCase(HackathonStatus.planning)]
        [TestCase(HackathonStatus.pendingApproval)]
        [TestCase(HackathonStatus.offline)]
        public async Task Publish_Succeeded(HackathonStatus status)
        {
            string name = "Foo";
            HackathonEntity entity = new HackathonEntity { Status = status };
            var role = new HackathonRoles { isAdmin = true };
            CancellationToken cancellationToken = CancellationToken.None;

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(m => m.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(entity);
            hackathonManagement.Setup(m => m.UpdateHackathonStatusAsync(entity, HackathonStatus.online, cancellationToken))
                .Callback<HackathonEntity, HackathonStatus, CancellationToken>((e, s, c) =>
                {
                    e.Status = s;
                })
                .ReturnsAsync(entity);
            hackathonManagement.Setup(h => h.GetHackathonRolesAsync(entity, null, cancellationToken))
               .ReturnsAsync(role);

            var controller = new HackathonController
            {
                HackathonManagement = hackathonManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
                ResponseBuilder = new DefaultResponseBuilder(),
            };
            var result = await controller.Publish(name, cancellationToken);

            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();

            var resp = AssertHelper.AssertOKResult<Hackathon>(result);
            Assert.AreEqual(HackathonStatus.online, resp.status);
        }
        #endregion

        #region UpdateReadonly
        [TestCase(true)]
        [TestCase(false)]
        public async Task UpdateReadonly(bool readOnly)
        {
            HackathonEntity entity = new HackathonEntity { };
            var role = new HackathonRoles { isAdmin = true };

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(m => m.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(entity);
            hackathonManagement.Setup(m => m.UpdateHackathonReadOnlyAsync(entity, readOnly, default))
                .Callback<HackathonEntity, bool, CancellationToken>((h, r, c) =>
                {
                    h.ReadOnly = r;
                })
                .ReturnsAsync(entity);
            hackathonManagement.Setup(h => h.GetHackathonRolesAsync(entity, null, default)).ReturnsAsync(role);

            var controller = new HackathonController
            {
                HackathonManagement = hackathonManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
            };
            var result = await controller.UpdateReadonly("Hack", readOnly, default);

            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();

            var resp = AssertHelper.AssertOKResult<Hackathon>(result);
            Assert.AreEqual(readOnly, resp.readOnly);
        }
        #endregion
    }
}
