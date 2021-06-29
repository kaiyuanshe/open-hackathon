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
using System.Security.Claims;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Controllers
{
    [TestFixture]
    public class EnrollmentControllerTests
    {
        #region Enroll
        [Test]
        public async Task EnrollTest_HackNotFound()
        {
            string hackathonName = "Hack";
            HackathonEntity hackathonEntity = null;
            CancellationToken cancellationToken = CancellationToken.None;

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", It.IsAny<CancellationToken>()))
                .ReturnsAsync(hackathonEntity);


            var controller = new EnrollmentController
            {
                HackathonManagement = hackathonManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.Enroll(hackathonName, null, cancellationToken);

            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 404);
        }

        [Test]
        public async Task EnrollTest_NotOnline()
        {
            string hackathonName = "Hack";
            HackathonEntity hackathonEntity = new HackathonEntity
            {
                Status = HackathonStatus.pendingApproval
            };
            CancellationToken cancellationToken = CancellationToken.None;

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", It.IsAny<CancellationToken>()))
                .ReturnsAsync(hackathonEntity);

            var controller = new EnrollmentController
            {
                HackathonManagement = hackathonManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.Enroll(hackathonName, null, cancellationToken);

            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 404);
        }

        [Test]
        public async Task EnrollTest_PreConditionFailed1()
        {
            string hackathonName = "Hack";
            HackathonEntity hackathonEntity = new HackathonEntity
            {
                EnrollmentStartedAt = DateTime.UtcNow.AddDays(1),
                Status = HackathonStatus.online,
            };
            CancellationToken cancellationToken = CancellationToken.None;

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", It.IsAny<CancellationToken>()))
                .ReturnsAsync(hackathonEntity);


            var controller = new EnrollmentController
            {
                HackathonManagement = hackathonManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.Enroll(hackathonName, null, cancellationToken);

            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 412);
        }

        [Test]
        public async Task EnrollTest_PreConditionFailed2()
        {
            string hackathonName = "Hack";
            HackathonEntity hackathonEntity = new HackathonEntity
            {
                EnrollmentStartedAt = DateTime.UtcNow.AddDays(-1),
                EnrollmentEndedAt = DateTime.UtcNow.AddDays(-1),
                Status = HackathonStatus.online,
            };
            CancellationToken cancellationToken = CancellationToken.None;

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", It.IsAny<CancellationToken>()))
                .ReturnsAsync(hackathonEntity);


            var controller = new EnrollmentController
            {
                HackathonManagement = hackathonManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.Enroll(hackathonName, null, cancellationToken);

            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 412);
        }

        [Test]
        public async Task EnrollTest_PreConditionFailed3()
        {
            string hackathonName = "Hack";
            HackathonEntity hackathonEntity = new HackathonEntity
            {
                EnrollmentStartedAt = DateTime.UtcNow.AddDays(-1),
                EnrollmentEndedAt = DateTime.UtcNow.AddDays(1),
                Status = HackathonStatus.online,
                Enrollment = 5,
                MaxEnrollment = 4,
            };
            CancellationToken cancellationToken = CancellationToken.None;

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", It.IsAny<CancellationToken>()))
                .ReturnsAsync(hackathonEntity);


            var controller = new EnrollmentController
            {
                HackathonManagement = hackathonManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.Enroll(hackathonName, null, cancellationToken);

            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 412, Resources.Enrollment_Full);
        }

        [Test]
        public async Task EnrollTest_Insert()
        {
            string hackathonName = "Hack";
            HackathonEntity hackathonEntity = new HackathonEntity
            {
                EnrollmentStartedAt = DateTime.UtcNow.AddDays(-1),
                EnrollmentEndedAt = DateTime.UtcNow.AddDays(1),
                Status = HackathonStatus.online,
                MaxEnrollment = 0,
            };
            Enrollment request = new Enrollment();
            EnrollmentEntity enrollment = new EnrollmentEntity { PartitionKey = "pk" };
            UserInfo userInfo = new UserInfo();
            CancellationToken cancellationToken = CancellationToken.None;

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", It.IsAny<CancellationToken>()))
                .ReturnsAsync(hackathonEntity);
            var enrollmentManagement = new Mock<IEnrollmentManagement>();
            enrollmentManagement.Setup(e => e.GetEnrollmentAsync("hack", "", cancellationToken)).ReturnsAsync(default(EnrollmentEntity));
            enrollmentManagement.Setup(p => p.CreateEnrollmentAsync(hackathonEntity, request, It.IsAny<CancellationToken>()))
                .ReturnsAsync(enrollment);
            var userManagement = new Mock<IUserManagement>();
            userManagement.Setup(p => p.GetUserByIdAsync(It.IsAny<string>(), cancellationToken))
                .ReturnsAsync(userInfo);

            var controller = new EnrollmentController
            {
                HackathonManagement = hackathonManagement.Object,
                UserManagement = userManagement.Object,
                EnrollmentManagement = enrollmentManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.Enroll(hackathonName, request, cancellationToken);

            Mock.VerifyAll(hackathonManagement, userManagement, enrollmentManagement);
            hackathonManagement.VerifyNoOtherCalls();
            userManagement.VerifyNoOtherCalls();
            enrollmentManagement.VerifyNoOtherCalls();
            Assert.IsTrue(result is OkObjectResult);
            OkObjectResult objectResult = (OkObjectResult)result;
            Enrollment en = (Enrollment)objectResult.Value;
            Assert.IsNotNull(en);
            Assert.AreEqual("pk", enrollment.HackathonName);
        }
        #endregion

        [Test]
        public async Task GetTest_NotFound()
        {
            string hackathonName = "hack";
            EnrollmentEntity enrollment = null;
            CancellationToken cancellationToken = default;

            var enrollmentManagement = new Mock<IEnrollmentManagement>();
            enrollmentManagement.Setup(p => p.GetEnrollmentAsync("hack", string.Empty, It.IsAny<CancellationToken>()))
                .ReturnsAsync(enrollment);

            var controller = new EnrollmentController
            {
                EnrollmentManagement = enrollmentManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.Get(hackathonName, cancellationToken);

            Mock.VerifyAll(enrollmentManagement);
            enrollmentManagement.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 404);
        }

        [Test]
        public async Task GetTest_Ok()
        {
            string hackathonName = "hack";
            EnrollmentEntity enrollment = new EnrollmentEntity { Status = EnrollmentStatus.pendingApproval };
            CancellationToken cancellationToken = default;
            UserInfo userInfo = new UserInfo();

            var enrollmentManagement = new Mock<IEnrollmentManagement>();
            enrollmentManagement.Setup(p => p.GetEnrollmentAsync("hack", string.Empty, It.IsAny<CancellationToken>()))
                .ReturnsAsync(enrollment);
            var userManagement = new Mock<IUserManagement>();
            userManagement.Setup(p => p.GetUserByIdAsync(It.IsAny<string>(), cancellationToken))
                .ReturnsAsync(userInfo);

            var controller = new EnrollmentController
            {
                EnrollmentManagement = enrollmentManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
                UserManagement = userManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.Get(hackathonName, cancellationToken);

            Mock.VerifyAll(enrollmentManagement, userManagement);
            enrollmentManagement.VerifyNoOtherCalls();
            userManagement.VerifyNoOtherCalls();

            Assert.IsTrue(result is OkObjectResult);
            OkObjectResult objectResult = (OkObjectResult)result;
            Enrollment en = (Enrollment)objectResult.Value;
            Assert.IsNotNull(en);
            Assert.AreEqual(EnrollmentStatus.pendingApproval, enrollment.Status);
        }

        private static IEnumerable ListStatus()
        {
            yield return EnrollmentStatus.approved;
            yield return EnrollmentStatus.rejected;
        }

        private static Func<string, string, Enrollment, CancellationToken, Task<object>> GetTargetMethod(EnrollmentController controller, EnrollmentStatus status)
        {
            if (status == EnrollmentStatus.approved)
                return controller.Approve;

            if (status == EnrollmentStatus.rejected)
                return controller.Reject;

            return null;
        }

        [Test, TestCaseSource(nameof(ListStatus))]
        public async Task ApproveRejectTest_HackNotFound(EnrollmentStatus status)
        {
            string hack = "Hack";
            string userId = "Uid";
            HackathonEntity hackathonEntity = null;
            CancellationToken cancellationToken = default;

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", It.IsAny<CancellationToken>()))
                .ReturnsAsync(hackathonEntity);

            var controller = new EnrollmentController
            {
                HackathonManagement = hackathonManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var func = GetTargetMethod(controller, status);
            var result = await func(hack, userId, null, cancellationToken);

            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 404);
        }

        [Test, TestCaseSource(nameof(ListStatus))]
        public async Task ApproveRejectTest_Forbidden(EnrollmentStatus status)
        {
            string hack = "Hack";
            string userId = "Uid";
            HackathonEntity hackathonEntity = new HackathonEntity();
            var authResult = AuthorizationResult.Failed();
            CancellationToken cancellationToken = default;

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", It.IsAny<CancellationToken>()))
                .ReturnsAsync(hackathonEntity);

            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), hackathonEntity, AuthConstant.Policy.HackathonAdministrator))
                .ReturnsAsync(authResult);

            var controller = new EnrollmentController
            {
                HackathonManagement = hackathonManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
                AuthorizationService = authorizationService.Object,
            };
            var func = GetTargetMethod(controller, status);
            var result = await func(hack, userId, null, cancellationToken);

            Mock.VerifyAll(hackathonManagement, authorizationService);
            hackathonManagement.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 403);
        }

        [Test, TestCaseSource(nameof(ListStatus))]
        public async Task ApproveRejectTest_EnrollmentNotFound(EnrollmentStatus status)
        {
            string hack = "Hack";
            string userId = "Uid";
            HackathonEntity hackathonEntity = new HackathonEntity();
            var authResult = AuthorizationResult.Success();
            EnrollmentEntity participant = null;
            CancellationToken cancellationToken = default;

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", It.IsAny<CancellationToken>()))
                .ReturnsAsync(hackathonEntity);
            var enrollmentManagement = new Mock<IEnrollmentManagement>();
            enrollmentManagement.Setup(p => p.GetEnrollmentAsync("hack", "uid", It.IsAny<CancellationToken>()))
                .ReturnsAsync(participant);

            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), hackathonEntity, AuthConstant.Policy.HackathonAdministrator))
                .ReturnsAsync(authResult);

            var controller = new EnrollmentController
            {
                HackathonManagement = hackathonManagement.Object,
                EnrollmentManagement = enrollmentManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
                AuthorizationService = authorizationService.Object,
            };
            var func = GetTargetMethod(controller, status);
            var result = await func(hack, userId, null, cancellationToken);

            Mock.VerifyAll(hackathonManagement, authorizationService);
            hackathonManagement.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 404);
        }

        [Test, TestCaseSource(nameof(ListStatus))]
        public async Task ApproveRejectTest_Succeeded(EnrollmentStatus status)
        {
            string hack = "Hack";
            string userId = "Uid";
            HackathonEntity hackathonEntity = new HackathonEntity();
            var authResult = AuthorizationResult.Success();
            EnrollmentEntity participant = new EnrollmentEntity
            {
                Status = EnrollmentStatus.pendingApproval,
            };
            CancellationToken cancellationToken = default;
            UserInfo userInfo = new UserInfo();

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", It.IsAny<CancellationToken>()))
                .ReturnsAsync(hackathonEntity);
            var enrollmentManagement = new Mock<IEnrollmentManagement>();
            enrollmentManagement.Setup(p => p.GetEnrollmentAsync("hack", "uid", It.IsAny<CancellationToken>()))
                .ReturnsAsync(participant);
            enrollmentManagement.Setup(p => p.UpdateEnrollmentStatusAsync(hackathonEntity, It.IsAny<EnrollmentEntity>(), It.IsAny<EnrollmentStatus>(), It.IsAny<CancellationToken>()))
                            .Callback<HackathonEntity, EnrollmentEntity, EnrollmentStatus, CancellationToken>((h, p, e, c) =>
                            {
                                p.Status = e;
                            })
                            .ReturnsAsync(participant);
            var userManagement = new Mock<IUserManagement>();
            userManagement.Setup(p => p.GetUserByIdAsync(It.IsAny<string>(), cancellationToken))
                .ReturnsAsync(userInfo);

            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), hackathonEntity, AuthConstant.Policy.HackathonAdministrator))
                .ReturnsAsync(authResult);

            var controller = new EnrollmentController
            {
                HackathonManagement = hackathonManagement.Object,
                EnrollmentManagement = enrollmentManagement.Object,
                UserManagement = userManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
                AuthorizationService = authorizationService.Object,
            };
            var func = GetTargetMethod(controller, status);
            var result = await func(hack, userId, null, cancellationToken);

            Mock.VerifyAll(hackathonManagement, authorizationService, userManagement, enrollmentManagement);
            hackathonManagement.VerifyNoOtherCalls();
            userManagement.VerifyNoOtherCalls();
            enrollmentManagement.VerifyNoOtherCalls();
            Assert.IsTrue(result is OkObjectResult);
            OkObjectResult objectResult = (OkObjectResult)result;
            Enrollment enrollment = (Enrollment)objectResult.Value;
            Assert.IsNotNull(enrollment);
            Assert.AreEqual(status, enrollment.status);
        }

        [Test]
        public async Task GetById_HackNotFound()
        {
            string hack = "Hack";
            string userId = "Uid";
            HackathonEntity hackathonEntity = null;
            CancellationToken cancellationToken = default;

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", It.IsAny<CancellationToken>()))
                .ReturnsAsync(hackathonEntity);

            var controller = new EnrollmentController
            {
                HackathonManagement = hackathonManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.GetById(hack, userId, cancellationToken);

            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 404);
        }

        [Test]
        public async Task GetById_EnrollmentNotFound()
        {
            string hack = "Hack";
            string userId = "Uid";
            HackathonEntity hackathonEntity = new HackathonEntity();
            var authResult = AuthorizationResult.Success();
            EnrollmentEntity enrollment = null;
            CancellationToken cancellationToken = default;

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", It.IsAny<CancellationToken>()))
                .ReturnsAsync(hackathonEntity);
            var enrollmentManagement = new Mock<IEnrollmentManagement>();
            enrollmentManagement.Setup(p => p.GetEnrollmentAsync("hack", "uid", It.IsAny<CancellationToken>()))
                .ReturnsAsync(enrollment);

            var controller = new EnrollmentController
            {
                HackathonManagement = hackathonManagement.Object,
                EnrollmentManagement = enrollmentManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.GetById(hack, userId, cancellationToken);

            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 404);
        }

        [Test]
        public async Task GetById_Succeeded()
        {
            string hack = "Hack";
            string userId = "Uid";
            HackathonEntity hackathonEntity = new HackathonEntity();
            var authResult = AuthorizationResult.Success();
            EnrollmentEntity participant = new EnrollmentEntity
            {
                Status = EnrollmentStatus.pendingApproval,
            };
            CancellationToken cancellationToken = default;
            UserInfo userInfo = new UserInfo();

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", It.IsAny<CancellationToken>()))
                .ReturnsAsync(hackathonEntity);
            var enrollmentManagement = new Mock<IEnrollmentManagement>();
            enrollmentManagement.Setup(p => p.GetEnrollmentAsync("hack", "uid", It.IsAny<CancellationToken>()))
                .ReturnsAsync(participant);
            var userManagement = new Mock<IUserManagement>();
            userManagement.Setup(p => p.GetUserByIdAsync(It.IsAny<string>(), cancellationToken))
                .ReturnsAsync(userInfo);

            var controller = new EnrollmentController
            {
                HackathonManagement = hackathonManagement.Object,
                EnrollmentManagement = enrollmentManagement.Object,
                UserManagement = userManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.GetById(hack, userId, cancellationToken);

            Mock.VerifyAll(hackathonManagement, userManagement);
            hackathonManagement.VerifyNoOtherCalls();
            userManagement.VerifyNoOtherCalls();
            Assert.IsTrue(result is OkObjectResult);
            OkObjectResult objectResult = (OkObjectResult)result;
            Enrollment enrollment = (Enrollment)objectResult.Value;
            Assert.IsNotNull(enrollment);
            Assert.AreEqual(EnrollmentStatus.pendingApproval, enrollment.status);
        }

        [Test]
        public async Task ListEnrollmentsTest_HackNotFound()
        {
            string hack = "Hack";
            Pagination pagination = new Pagination();
            CancellationToken cancellationToken = CancellationToken.None;
            HackathonEntity hackathonEntity = null;

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", It.IsAny<CancellationToken>()))
                .ReturnsAsync(hackathonEntity);

            var controller = new EnrollmentController
            {
                HackathonManagement = hackathonManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.ListEnrollments(hack, pagination, null, cancellationToken);

            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 404);
        }

        private static IEnumerable ListEnrollmentsTestData()
        {
            // arg0: pagination
            // arg1: status
            // arg2: mocked TableCotinuationToken
            // arg3: expected options
            // arg4: expected nextlink

            // no pagination, no filter, no top
            yield return new TestCaseData(
                    new Pagination { },
                    null,
                    null,
                    new EnrollmentQueryOptions { },
                    null
                );

            // with pagination and filters
            yield return new TestCaseData(
                    new Pagination { top = 10, np = "np", nr = "nr" },
                    EnrollmentStatus.rejected,
                    null,
                    new EnrollmentQueryOptions
                    {
                        Top = 10,
                        TableContinuationToken = new TableContinuationToken
                        {
                            NextPartitionKey = "np",
                            NextRowKey = "nr"
                        },
                        Status = EnrollmentStatus.rejected
                    },
                    null
                );

            // next link
            yield return new TestCaseData(
                    new Pagination { },
                    null,
                    new TableContinuationToken
                    {
                        NextPartitionKey = "np",
                        NextRowKey = "nr"
                    },
                    new EnrollmentQueryOptions { },
                    "&np=np&nr=nr"
                );
        }

        [Test, TestCaseSource(nameof(ListEnrollmentsTestData))]
        public async Task ListEnrollmentsTest_Succeed(
            Pagination pagination,
            EnrollmentStatus? status,
            TableContinuationToken continuationToken,
            EnrollmentQueryOptions expectedOptions,
            string expectedLink)
        {
            // input
            var hackName = "Hack";
            var cancellationToken = CancellationToken.None;
            HackathonEntity hackathonEntity = new HackathonEntity();
            var enrollments = new List<EnrollmentEntity>
            {
                new EnrollmentEntity
                {
                    PartitionKey = "pk",
                    RowKey = "rk",
                    Status = EnrollmentStatus.approved,
                }
            };
            var segment = MockHelper.CreateTableQuerySegment(enrollments, continuationToken);
            UserInfo userInfo = new UserInfo();

            // mock and capture
            var hackathonManagement = new Mock<IHackathonManagement>();
            EnrollmentQueryOptions optionsCaptured = null;
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", It.IsAny<CancellationToken>()))
                .ReturnsAsync(hackathonEntity);
            var enrollmentManagement = new Mock<IEnrollmentManagement>();
            enrollmentManagement.Setup(p => p.ListPaginatedEnrollmentsAsync("hack", It.IsAny<EnrollmentQueryOptions>(), cancellationToken))
                .Callback<string, EnrollmentQueryOptions, CancellationToken>((n, o, t) =>
                {
                    optionsCaptured = o;
                })
                .ReturnsAsync(segment);
            var userManagement = new Mock<IUserManagement>();
            userManagement.Setup(p => p.GetUserByIdAsync(It.IsAny<string>(), cancellationToken))
                .ReturnsAsync(userInfo);

            // run
            var controller = new EnrollmentController
            {
                ResponseBuilder = new DefaultResponseBuilder(),
                HackathonManagement = hackathonManagement.Object,
                EnrollmentManagement = enrollmentManagement.Object,
                UserManagement = userManagement.Object,
            };
            var result = await controller.ListEnrollments(hackName, pagination, status, cancellationToken);

            // verify
            Mock.VerifyAll(hackathonManagement, userManagement);
            hackathonManagement.VerifyNoOtherCalls();
            userManagement.VerifyNoOtherCalls();
            var list = AssertHelper.AssertOKResult<EnrollmentList>(result);
            Assert.AreEqual(expectedLink, list.nextLink);
            Assert.AreEqual(1, list.value.Length);
            Assert.AreEqual("pk", list.value[0].hackathonName);
            Assert.AreEqual("rk", list.value[0].userId);
            Assert.AreEqual(EnrollmentStatus.approved, list.value[0].status);
            Assert.AreEqual(expectedOptions.Status, optionsCaptured.Status);
            Assert.AreEqual(expectedOptions.Top, optionsCaptured.Top);
            Assert.AreEqual(expectedOptions.TableContinuationToken?.NextPartitionKey, optionsCaptured.TableContinuationToken?.NextPartitionKey);
            Assert.AreEqual(expectedOptions.TableContinuationToken?.NextRowKey, optionsCaptured.TableContinuationToken?.NextRowKey);
        }

        #region GetHackathonRolesAsync
        [Test]
        public async Task GetHackathonRolesAsyncTest_NoUserIdClaim()
        {
            HackathonEntity hackathon = new HackathonEntity { PartitionKey = "hack" };
            ClaimsPrincipal user = new ClaimsPrincipal();
            ClaimsPrincipal user2 = new ClaimsPrincipal(new ClaimsIdentity(new List<Claim>
            {
                new Claim(AuthConstant.ClaimType.PlatformAdministrator, "uid"),
            }));
            CancellationToken cancellationToken = CancellationToken.None;

            var hackathonManagement = new HackathonManagement(null);
            Assert.IsNull(await hackathonManagement.GetHackathonRolesAsync(hackathon, null, cancellationToken));
            Assert.IsNull(await hackathonManagement.GetHackathonRolesAsync(hackathon, user, cancellationToken));
            Assert.IsNull(await hackathonManagement.GetHackathonRolesAsync(hackathon, user2, cancellationToken));
            Assert.IsNull(await hackathonManagement.GetHackathonRolesAsync(null, user, cancellationToken));
        }

        private static IEnumerable GetHackathonRolesAsyncTestData()
        {
            // arg0: user
            // arg1: admins
            // arg2: enrolled
            // expected roles

            // platform admin
            yield return new TestCaseData(
                new ClaimsPrincipal(new ClaimsIdentity(new List<Claim>
                {
                    new Claim(AuthConstant.ClaimType.UserId, "uid"),
                    new Claim(AuthConstant.ClaimType.PlatformAdministrator, "uid"),
                })),
                null,
                false,
                new HackathonRoles
                {
                    isAdmin = true,
                    isEnrolled = false,
                    isJudge = false
                });

            // hack admin
            yield return new TestCaseData(
                new ClaimsPrincipal(new ClaimsIdentity(new List<Claim>
                {
                    new Claim(AuthConstant.ClaimType.UserId, "uid"),
                })),
                new List<HackathonAdminEntity>
                {
                    new HackathonAdminEntity { PartitionKey="hack", RowKey="uid" },
                },
                false,
                new HackathonRoles
                {
                    isAdmin = true,
                    isEnrolled = false,
                    isJudge = false
                });

            // neither platform nor hack admin
            yield return new TestCaseData(
                new ClaimsPrincipal(new ClaimsIdentity(new List<Claim>
                {
                    new Claim(AuthConstant.ClaimType.UserId, "uid"),
                })),
                new List<HackathonAdminEntity>
                {
                    new HackathonAdminEntity { PartitionKey="hack", RowKey="other" },
                    new HackathonAdminEntity { PartitionKey="hack", RowKey="other2" }
                },
                false,
                new HackathonRoles
                {
                    isAdmin = false,
                    isEnrolled = false,
                    isJudge = false
                });

            // enrolled
            yield return new TestCaseData(
                new ClaimsPrincipal(new ClaimsIdentity(new List<Claim>
                {
                    new Claim(AuthConstant.ClaimType.UserId, "uid"),
                    new Claim(AuthConstant.ClaimType.PlatformAdministrator, "uid"),
                })),
                null,
                true,
                new HackathonRoles
                {
                    isAdmin = true,
                    isEnrolled = true,
                    isJudge = false
                });
        }

        [Test, TestCaseSource(nameof(GetHackathonRolesAsyncTestData))]
        public async Task GetHackathonRolesAsync(ClaimsPrincipal user, IEnumerable<HackathonAdminEntity> admins, bool enrolled, HackathonRoles expectedRoles)
        {
            HackathonEntity hackathon = new HackathonEntity { PartitionKey = "hack" };

            var hackathonAdminManagement = new Mock<IHackathonAdminManagement>();
            if (admins != null)
            {
                hackathonAdminManagement.Setup(h => h.ListHackathonAdminAsync(hackathon.Name, default)).ReturnsAsync(admins);
            }
            var enrollmentManagement = new Mock<IEnrollmentManagement>();
            enrollmentManagement.Setup(h => h.IsUserEnrolledAsync(hackathon, "uid", default)).ReturnsAsync(enrolled);

            var hackathonManagement = new HackathonManagement(null)
            {
                EnrollmentManagement = enrollmentManagement.Object,
                HackathonAdminManagement = hackathonAdminManagement.Object,
            };
            var role = await hackathonManagement.GetHackathonRolesAsync(hackathon, user, default);

            Mock.VerifyAll(enrollmentManagement, hackathonAdminManagement);
            enrollmentManagement.VerifyNoOtherCalls();
            hackathonAdminManagement.VerifyNoOtherCalls();

            Assert.AreEqual(expectedRoles.isAdmin, role.isAdmin);
            Assert.AreEqual(expectedRoles.isEnrolled, role.isEnrolled);
            Assert.AreEqual(expectedRoles.isJudge, role.isJudge);
        }
        #endregion
    }
}
