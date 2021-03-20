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
using System;
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
            Assert.IsTrue(result is ObjectResult);
            ObjectResult objectResult = (ObjectResult)result;
            Assert.AreEqual(404, objectResult.StatusCode.Value);
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
            Assert.IsTrue(result is ObjectResult);
            ObjectResult objectResult = (ObjectResult)result;
            Assert.AreEqual(412, objectResult.StatusCode.Value);
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
            Assert.IsTrue(result is ObjectResult);
            ObjectResult objectResult = (ObjectResult)result;
            Assert.AreEqual(412, objectResult.StatusCode.Value);
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
            ParticipantEntity participant = new ParticipantEntity { PartitionKey = "pk" };

            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", It.IsAny<CancellationToken>()))
                .ReturnsAsync(hackathonEntity);
            hackathonManagement.Setup(p => p.EnrollAsync(hackathonEntity, string.Empty, It.IsAny<CancellationToken>()))
                .ReturnsAsync(participant);

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
            Enrollment enrollment = (Enrollment)objectResult.Value;
            Assert.IsNotNull(enrollment);
            Assert.AreEqual("pk", enrollment.hackathonName);
        }
    }
}
