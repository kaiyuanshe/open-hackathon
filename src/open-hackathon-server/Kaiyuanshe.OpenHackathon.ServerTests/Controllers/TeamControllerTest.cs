using Kaiyuanshe.OpenHackathon.Server;
using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Controllers;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.ResponseBuilder;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.AspNetCore.Mvc;
using Moq;
using NUnit.Framework;
using System;
using System.Collections.Generic;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Controllers
{
    [TestFixture]
    public class TeamControllerTest
    {
        [Test]
        public async Task Create_HackNotFound()
        {
            // input
            string hackName = "Foo";
            HackathonEntity hackathon = null;
            Team parameter = new Team { };
            CancellationToken cancellationToken = CancellationToken.None;
            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(hackathon);
            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.Create(hackName, parameter, cancellationToken);
            // verify
            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 404, string.Format(Resources.Hackathon_NotFound, hackName));
        }

        [Test]
        public async Task Create_HackNotOnline()
        {
            // input
            string hackName = "Foo";
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.planning };
            Team parameter = new Team { };
            CancellationToken cancellationToken = CancellationToken.None;
            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(hackathon);
            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.Create(hackName, parameter, cancellationToken);
            // verify
            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 404, string.Format(Resources.Hackathon_NotFound, hackName));
        }

        [Test]
        public async Task Create_NotEnrolled()
        {
            // input
            string hackName = "Foo";
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            EnrollmentEntity enrollment = null;
            Team parameter = new Team { };
            CancellationToken cancellationToken = CancellationToken.None;

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(hackathon);
            hackathonManagement.Setup(p => p.GetEnrollmentAsync("foo", "", cancellationToken)).ReturnsAsync(enrollment);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.Create(hackName, parameter, cancellationToken);

            // verify
            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 404, string.Format(Resources.Hackathon_Enrollment_NotFound, "", hackName));
        }

        [Test]
        public async Task Create_EnrollmentNotApproved()
        {
            // input
            string hackName = "Foo";
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            EnrollmentEntity enrollment = new EnrollmentEntity { Status = EnrollmentStatus.pendingApproval };
            Team parameter = new Team { };
            CancellationToken cancellationToken = CancellationToken.None;

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(hackathon);
            hackathonManagement.Setup(p => p.GetEnrollmentAsync("foo", "", cancellationToken)).ReturnsAsync(enrollment);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.Create(hackName, parameter, cancellationToken);

            // verify
            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 412, Resources.Hackathon_Enrollment_NotApproved);
        }

        [Test]
        public async Task Create_Created()
        {
            // input
            string hackName = "Foo";
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            EnrollmentEntity enrollment = new EnrollmentEntity { Status = EnrollmentStatus.approved };
            Team parameter = new Team { };
            TeamEntity teamEntity = new TeamEntity { AutoApprove = true, CreatorId = "uid", PartitionKey = "pk", RowKey = "rk" };
            CancellationToken cancellationToken = CancellationToken.None;

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(hackathon);
            hackathonManagement.Setup(p => p.GetEnrollmentAsync("foo", "", cancellationToken)).ReturnsAsync(enrollment);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.CreateTeamAsync(parameter, cancellationToken)).ReturnsAsync(teamEntity);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                TeamManagement = teamManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
                ResponseBuilder = new DefaultResponseBuilder(),
            };
            var result = await controller.Create(hackName, parameter, cancellationToken);

            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            Assert.AreEqual("foo", parameter.hackathonName);
            Assert.AreEqual("", parameter.creatorId);
            Assert.IsTrue(result is OkObjectResult);
            OkObjectResult objectResult = (OkObjectResult)result;
            Assert.IsTrue(objectResult.Value is Team);
            Team resp = (Team)objectResult.Value;
            Assert.AreEqual(true, resp.autoApprove.Value);
            Assert.AreEqual("uid", resp.creatorId);
            Assert.AreEqual("pk", resp.hackathonName);
            Assert.AreEqual("rk", resp.id);
        }
    }
}
