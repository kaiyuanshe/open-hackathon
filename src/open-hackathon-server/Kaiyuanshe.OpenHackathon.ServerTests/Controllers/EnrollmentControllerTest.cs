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
using System;
using System.Collections;
using System.Security.Claims;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Controllers
{
    [TestFixture]
    public class EnrollmentControllerTest
    {
        [Test]
        public async Task EnrollTest_NotFound()
        {
            string hackathonName = "Hack";
            HackathonEntity hackathonEntity = null;

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", It.IsAny<CancellationToken>()))
                .ReturnsAsync(hackathonEntity);


            var controller = new EnrollmentController
            {
                HackathonManagement = hackathonManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.Enroll(hackathonName, null);

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
            };

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", It.IsAny<CancellationToken>()))
                .ReturnsAsync(hackathonEntity);


            var controller = new EnrollmentController
            {
                HackathonManagement = hackathonManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.Enroll(hackathonName, null);

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
            };

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", It.IsAny<CancellationToken>()))
                .ReturnsAsync(hackathonEntity);


            var controller = new EnrollmentController
            {
                HackathonManagement = hackathonManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.Enroll(hackathonName, null);

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
            };
            EnrollmentEntity enrollment = new EnrollmentEntity { PartitionKey = "pk" };

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
            var result = await controller.Enroll(hackathonName, null);

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
        public async Task GetByAdmin_HackNotFound()
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
            var result = await controller.GetByAdmin(hack, userId);

            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 404);
        }

        [Test]
        public async Task GetByAdmin_Forbidden()
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
            var result = await controller.GetByAdmin(hack, userId);

            Mock.VerifyAll(hackathonManagement, authorizationService);
            hackathonManagement.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 403);
        }

        [Test]
        public async Task GetByAdmin_EnrollmentNotFound()
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
            var result = await controller.GetByAdmin(hack, userId);

            Mock.VerifyAll(hackathonManagement, authorizationService);
            hackathonManagement.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 404);
        }

        [Test]
        public async Task GetByAdmin_Succeeded()
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
            var result = await controller.GetByAdmin(hack, userId);

            Mock.VerifyAll(hackathonManagement, authorizationService);
            hackathonManagement.VerifyNoOtherCalls();
            Assert.IsTrue(result is OkObjectResult);
            OkObjectResult objectResult = (OkObjectResult)result;
            Enrollment enrollment = (Enrollment)objectResult.Value;
            Assert.IsNotNull(enrollment);
            Assert.AreEqual(EnrollmentStatus.pendingApproval, enrollment.status);
        }
    }
}
