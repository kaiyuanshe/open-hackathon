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
        [Test]
        public async Task EnrollTest_NotFound()
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
        public async Task EnrollTest_Enrolled()
        {
            string hackathonName = "Hack";
            HackathonEntity hackathonEntity = new HackathonEntity
            {
                EnrollmentStartedAt = DateTime.UtcNow.AddDays(-1),
                EnrollmentEndedAt = DateTime.UtcNow.AddDays(1),
                Status = HackathonStatus.online,
            };
            EnrollmentEntity enrollment = new EnrollmentEntity { PartitionKey = "pk" };
            CancellationToken cancellationToken = CancellationToken.None;

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", It.IsAny<CancellationToken>()))
                .ReturnsAsync(hackathonEntity);
            hackathonManagement.Setup(p => p.EnrollAsync(hackathonEntity, string.Empty, It.IsAny<CancellationToken>()))
                .ReturnsAsync(enrollment);

            var controller = new EnrollmentController
            {
                HackathonManagement = hackathonManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.Enroll(hackathonName, null, cancellationToken);

            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            Assert.IsTrue(result is OkObjectResult);
            OkObjectResult objectResult = (OkObjectResult)result;
            Enrollment en = (Enrollment)objectResult.Value;
            Assert.IsNotNull(en);
            Assert.AreEqual("pk", enrollment.HackathonName);
        }

        [Test]
        public async Task GetTest_NotFound()
        {
            string hackathonName = "hack";
            EnrollmentEntity enrollment = null;

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetEnrollmentAsync("hack", string.Empty, It.IsAny<CancellationToken>()))
                .ReturnsAsync(enrollment);

            var controller = new EnrollmentController
            {
                HackathonManagement = hackathonManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.Get(hackathonName);

            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 404);
        }

        [Test]
        public async Task GetTest_Ok()
        {
            string hackathonName = "hack";
            EnrollmentEntity enrollment = new EnrollmentEntity { Status = EnrollmentStatus.pendingApproval };

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetEnrollmentAsync("hack", string.Empty, It.IsAny<CancellationToken>()))
                .ReturnsAsync(enrollment);

            var controller = new EnrollmentController
            {
                HackathonManagement = hackathonManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.Get(hackathonName);

            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
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

        private static Func<string, string, Enrollment, Task<object>> GetTargetMethod(EnrollmentController controller, EnrollmentStatus status)
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
            var result = await func(hack, userId, null);

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
            var result = await func(hack, userId, null);

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

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", It.IsAny<CancellationToken>()))
                .ReturnsAsync(hackathonEntity);
            hackathonManagement.Setup(p => p.GetEnrollmentAsync("hack", "uid", It.IsAny<CancellationToken>()))
                .ReturnsAsync(participant);

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
            var result = await func(hack, userId, null);

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

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", It.IsAny<CancellationToken>()))
                .ReturnsAsync(hackathonEntity);
            hackathonManagement.Setup(p => p.GetEnrollmentAsync("hack", "uid", It.IsAny<CancellationToken>()))
                .ReturnsAsync(participant);
            hackathonManagement.Setup(p => p.UpdateEnrollmentStatusAsync(It.IsAny<EnrollmentEntity>(), It.IsAny<EnrollmentStatus>(), It.IsAny<CancellationToken>()))
                            .Callback<EnrollmentEntity, EnrollmentStatus, CancellationToken>((p, e, c) =>
                            {
                                p.Status = e;
                            })
                            .ReturnsAsync(participant);

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
            var result = await func(hack, userId, null);

            Mock.VerifyAll(hackathonManagement, authorizationService);
            hackathonManagement.VerifyNoOtherCalls();
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

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", It.IsAny<CancellationToken>()))
                .ReturnsAsync(hackathonEntity);

            var controller = new EnrollmentController
            {
                HackathonManagement = hackathonManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.GetById(hack, userId);

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

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", It.IsAny<CancellationToken>()))
                .ReturnsAsync(hackathonEntity);
            hackathonManagement.Setup(p => p.GetEnrollmentAsync("hack", "uid", It.IsAny<CancellationToken>()))
                .ReturnsAsync(enrollment);

            var controller = new EnrollmentController
            {
                HackathonManagement = hackathonManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.GetById(hack, userId);

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

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", It.IsAny<CancellationToken>()))
                .ReturnsAsync(hackathonEntity);
            hackathonManagement.Setup(p => p.GetEnrollmentAsync("hack", "uid", It.IsAny<CancellationToken>()))
                .ReturnsAsync(participant);

            var controller = new EnrollmentController
            {
                HackathonManagement = hackathonManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.GetById(hack, userId);

            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
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

            // mock and capture
            var hackathonManagement = new Mock<IHackathonManagement>();
            EnrollmentQueryOptions optionsCaptured = null;
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", It.IsAny<CancellationToken>()))
                .ReturnsAsync(hackathonEntity);
            hackathonManagement.Setup(p => p.ListPaginatedEnrollmentsAsync("hack", It.IsAny<EnrollmentQueryOptions>(), cancellationToken))
                .Callback<string, EnrollmentQueryOptions, CancellationToken>((n, o, t) =>
                {
                    optionsCaptured = o;
                })
                .ReturnsAsync(segment);

            // run
            var controller = new EnrollmentController
            {
                ResponseBuilder = new DefaultResponseBuilder(),
                HackathonManagement = hackathonManagement.Object,
            };
            var result = await controller.ListEnrollments(hackName, pagination, status, cancellationToken);

            // verify
            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
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

        [Test]
        public async Task GetHackathonRolesAsyncTest_NoUserIdClaim()
        {
            string hackName = "hack";
            ClaimsPrincipal user = new ClaimsPrincipal();
            ClaimsPrincipal user2 = new ClaimsPrincipal(new ClaimsIdentity(new List<Claim>
            {
                new Claim(AuthConstant.ClaimType.PlatformAdministrator, "uid"),
            }));
            CancellationToken cancellationToken = CancellationToken.None;

            var hackathonManagement = new HackathonManagement(null);
            Assert.IsNull(await hackathonManagement.GetHackathonRolesAsync(hackName, null, cancellationToken));
            Assert.IsNull(await hackathonManagement.GetHackathonRolesAsync(hackName, user, cancellationToken));
            Assert.IsNull(await hackathonManagement.GetHackathonRolesAsync(hackName, user2, cancellationToken));
        }

        [Test]
        public async Task GetHackathonRolesAsyncTest_PlatformAdmin()
        {
            string hackName = "hack";
            ClaimsPrincipal user = new ClaimsPrincipal(new ClaimsIdentity(new List<Claim>
            {
                new Claim(AuthConstant.ClaimType.UserId, "uid"),
                new Claim(AuthConstant.ClaimType.PlatformAdministrator, "uid"),
            }));
            CancellationToken cancellationToken = CancellationToken.None;
            EnrollmentEntity enrollment = null;

            var hackathonManagement = new Mock<HackathonManagement>(null) { CallBase = true };
            hackathonManagement.Setup(h => h.GetEnrollmentAsync("hack", "uid", cancellationToken)).ReturnsAsync(enrollment);
            var role = await hackathonManagement.Object.GetHackathonRolesAsync(hackName, user, cancellationToken);

            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            Assert.IsNotNull(role);
            Assert.IsTrue(role.isAdmin);
            Assert.IsFalse(role.isEnrolled);
            Assert.IsFalse(role.isJudge);
        }

        [Test]
        public async Task GetHackathonRolesAsyncTest_NotHackAdmin()
        {
            string hackName = "hack";
            ClaimsPrincipal user = new ClaimsPrincipal(new ClaimsIdentity(new List<Claim>
            {
                new Claim(AuthConstant.ClaimType.UserId, "uid"),
            }));
            CancellationToken cancellationToken = CancellationToken.None;
            EnrollmentEntity enrollment = null;
            List<HackathonAdminEntity> admins = new List<HackathonAdminEntity> {
                new HackathonAdminEntity{ RowKey = "anotherid" }
            };

            var hackathonAdminManagement = new Mock<IHackathonAdminManagement>();
            hackathonAdminManagement.Setup(h => h.ListHackathonAdminAsync(hackName, cancellationToken)).ReturnsAsync(admins);

            var hackathonManagement = new Mock<HackathonManagement>(null) { CallBase = true };
            hackathonManagement.Object.HackathonAdminManagement = hackathonAdminManagement.Object;
            hackathonManagement.Setup(h => h.GetEnrollmentAsync("hack", "uid", cancellationToken)).ReturnsAsync(enrollment);
            var role = await hackathonManagement.Object.GetHackathonRolesAsync(hackName, user, cancellationToken);

            Mock.VerifyAll(hackathonManagement, hackathonAdminManagement);
            hackathonManagement.VerifyNoOtherCalls();
            hackathonAdminManagement.VerifyNoOtherCalls();

            Assert.IsNotNull(role);
            Assert.IsFalse(role.isAdmin);
            Assert.IsFalse(role.isEnrolled);
            Assert.IsFalse(role.isJudge);
        }

        [Test]
        public async Task GetHackathonRolesAsyncTest_HackAdmin()
        {
            string hackName = "hack";
            ClaimsPrincipal user = new ClaimsPrincipal(new ClaimsIdentity(new List<Claim>
            {
                new Claim(AuthConstant.ClaimType.UserId, "uid"),
            }));
            CancellationToken cancellationToken = CancellationToken.None;
            EnrollmentEntity enrollment = null;
            List<HackathonAdminEntity> admins = new List<HackathonAdminEntity> {
                new HackathonAdminEntity{ RowKey = "uid" }
            };

            var hackathonAdminManagement = new Mock<IHackathonAdminManagement>();
            hackathonAdminManagement.Setup(h => h.ListHackathonAdminAsync(hackName, cancellationToken)).ReturnsAsync(admins);

            var hackathonManagement = new Mock<HackathonManagement>(null)
            {
                CallBase = true,
            };
            hackathonManagement.Object.HackathonAdminManagement = hackathonAdminManagement.Object;
            hackathonManagement.Setup(h => h.GetEnrollmentAsync("hack", "uid", cancellationToken)).ReturnsAsync(enrollment);
            var role = await hackathonManagement.Object.GetHackathonRolesAsync(hackName, user, cancellationToken);

            Mock.VerifyAll(hackathonManagement, hackathonAdminManagement);
            hackathonManagement.VerifyNoOtherCalls();
            hackathonAdminManagement.VerifyNoOtherCalls();
            Assert.IsNotNull(role);
            Assert.IsTrue(role.isAdmin);
            Assert.IsFalse(role.isEnrolled);
            Assert.IsFalse(role.isJudge);
        }

        [Test]
        public async Task GetHackathonRolesAsyncTest_EnrollmentNotApproved()
        {
            string hackName = "hack";
            ClaimsPrincipal user = new ClaimsPrincipal(new ClaimsIdentity(new List<Claim>
            {
                new Claim(AuthConstant.ClaimType.UserId, "uid"),
                new Claim(AuthConstant.ClaimType.PlatformAdministrator, "uid"),
            }));
            CancellationToken cancellationToken = CancellationToken.None;
            EnrollmentEntity enrollment = new EnrollmentEntity { Status = EnrollmentStatus.pendingApproval };

            var hackathonManagement = new Mock<HackathonManagement>(null) { CallBase = true };
            hackathonManagement.Setup(h => h.GetEnrollmentAsync("hack", "uid", cancellationToken)).ReturnsAsync(enrollment);
            var role = await hackathonManagement.Object.GetHackathonRolesAsync(hackName, user, cancellationToken);

            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            Assert.IsNotNull(role);
            Assert.IsTrue(role.isAdmin);
            Assert.IsFalse(role.isEnrolled);
            Assert.IsFalse(role.isJudge);
        }

        [Test]
        public async Task GetHackathonRolesAsyncTest_EnrollmentApproved()
        {
            string hackName = "hack";
            ClaimsPrincipal user = new ClaimsPrincipal(new ClaimsIdentity(new List<Claim>
            {
                new Claim(AuthConstant.ClaimType.UserId, "uid"),
                new Claim(AuthConstant.ClaimType.PlatformAdministrator, "uid"),
            }));
            CancellationToken cancellationToken = CancellationToken.None;
            EnrollmentEntity enrollment = new EnrollmentEntity { Status = EnrollmentStatus.approved };

            var hackathonManagement = new Mock<HackathonManagement>(null) { CallBase = true };
            hackathonManagement.Setup(h => h.GetEnrollmentAsync("hack", "uid", cancellationToken)).ReturnsAsync(enrollment);
            var role = await hackathonManagement.Object.GetHackathonRolesAsync(hackName, user, cancellationToken);

            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            Assert.IsNotNull(role);
            Assert.IsTrue(role.isAdmin);
            Assert.IsTrue(role.isEnrolled);
            Assert.IsFalse(role.isJudge);
        }
    }
}
