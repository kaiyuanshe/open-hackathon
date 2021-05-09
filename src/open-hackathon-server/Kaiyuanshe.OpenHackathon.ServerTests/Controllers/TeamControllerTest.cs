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
using System;
using System.Collections.Generic;
using System.Security.Claims;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Controllers
{
    [TestFixture]
    public class TeamControllerTest
    {
        [Test]
        public async Task CreateTeam_HackNotFound()
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
            var result = await controller.CreateTeam(hackName, parameter, cancellationToken);
            // verify
            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 404, string.Format(Resources.Hackathon_NotFound, hackName));
        }

        [Test]
        public async Task CreateTeam_HackNotOnline()
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
            var result = await controller.CreateTeam(hackName, parameter, cancellationToken);
            // verify
            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 404, string.Format(Resources.Hackathon_NotFound, hackName));
        }

        [Test]
        public async Task CreateTeam_HackNotStarted()
        {
            // input
            string hackName = "Foo";
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online, EventStartedAt = DateTime.UtcNow.AddDays(1) };
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
            var result = await controller.CreateTeam(hackName, parameter, cancellationToken);
            // verify
            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 412, Resources.Hackathon_NotStarted);
        }

        [Test]
        public async Task CreateTeam_HackEnded()
        {
            // input
            string hackName = "Foo";
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online, EventEndedAt = DateTime.UtcNow.AddDays(-1) };
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
            var result = await controller.CreateTeam(hackName, parameter, cancellationToken);
            // verify
            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 412, string.Format(Resources.Hackathon_Ended, hackathon.EventEndedAt));
        }

        [Test]
        public async Task CreateTeam_NotEnrolled()
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
            var result = await controller.CreateTeam(hackName, parameter, cancellationToken);

            // verify
            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 404, string.Format(Resources.Enrollment_NotFound, "", hackName));
        }

        [Test]
        public async Task CreateTeam_EnrollmentNotApproved()
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
            var result = await controller.CreateTeam(hackName, parameter, cancellationToken);

            // verify
            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 412, Resources.Enrollment_NotApproved);
        }

        [Test]
        public async Task CreateTeam_Created()
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
            var result = await controller.CreateTeam(hackName, parameter, cancellationToken);

            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            Assert.AreEqual("foo", parameter.hackathonName);
            Assert.AreEqual("", parameter.creatorId);
            Team resp = AssertHelper.AssertOKResult<Team>(result);
            Assert.AreEqual(true, resp.autoApprove.Value);
            Assert.AreEqual("uid", resp.creatorId);
            Assert.AreEqual("pk", resp.hackathonName);
            Assert.AreEqual("rk", resp.id);
        }

        [Test]
        public async Task UpdateTeam_HackNotFound()
        {
            // input
            string hackName = "Foo";
            string teamId = "tid";
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
            var result = await controller.UpdateTeam(hackName, teamId, parameter, cancellationToken);
            // verify
            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 404, string.Format(Resources.Hackathon_NotFound, hackName));
        }

        [Test]
        public async Task UpdateTeam_HackNotOnline()
        {
            // input
            string hackName = "Foo";
            string teamId = "tid";
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
            var result = await controller.UpdateTeam(hackName, teamId, parameter, cancellationToken);
            // verify
            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 404, string.Format(Resources.Hackathon_NotFound, hackName));
        }

        [Test]
        public async Task UpdateTeam_TeamNotFound()
        {
            // input
            string hackName = "Foo";
            string teamId = "tid";
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            Team parameter = new Team { };
            TeamEntity teamEntity = null;
            CancellationToken cancellationToken = CancellationToken.None;
            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(hackathon);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("foo", "tid", cancellationToken))
                .ReturnsAsync(teamEntity);
            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                TeamManagement = teamManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.UpdateTeam(hackName, teamId, parameter, cancellationToken);
            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 404, Resources.Team_NotFound);
        }

        [Test]
        public async Task UpdateTeam_TeamNotAdmin()
        {
            // input
            string hackName = "Foo";
            string teamId = "tid";
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            Team parameter = new Team { };
            TeamEntity teamEntity = new TeamEntity { };
            CancellationToken cancellationToken = CancellationToken.None;
            var authResult = AuthorizationResult.Failed();

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(hackathon);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("foo", "tid", cancellationToken))
                .ReturnsAsync(teamEntity);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), teamEntity, AuthConstant.Policy.TeamAdministrator))
                .ReturnsAsync(authResult);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                TeamManagement = teamManagement.Object,
                AuthorizationService = authorizationService.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.UpdateTeam(hackName, teamId, parameter, cancellationToken);
            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement, authorizationService);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 403, Resources.Team_NotAdmin);
        }

        [Test]
        public async Task UpdateTeam_Succeeded()
        {
            // input
            string hackName = "Foo";
            string teamId = "tid";
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            Team parameter = new Team { };
            TeamEntity teamEntity = new TeamEntity { };
            TeamEntity updated = new TeamEntity { Description = "updated" };
            CancellationToken cancellationToken = CancellationToken.None;
            var authResult = AuthorizationResult.Success();

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(hackathon);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("foo", "tid", cancellationToken))
                .ReturnsAsync(teamEntity);
            teamManagement.Setup(t => t.UpdateTeamAsync(parameter, teamEntity, cancellationToken))
                .ReturnsAsync(updated);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), teamEntity, AuthConstant.Policy.TeamAdministrator))
                .ReturnsAsync(authResult);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                TeamManagement = teamManagement.Object,
                AuthorizationService = authorizationService.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.UpdateTeam(hackName, teamId, parameter, cancellationToken);
            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement, authorizationService);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();

            Team output = AssertHelper.AssertOKResult<Team>(result);
            Assert.AreEqual("updated", output.description);
        }

        [Test]
        public async Task GetTeam_HackNotFound()
        {
            // input
            string hackName = "Foo";
            string teamId = "tid";
            HackathonEntity hackathon = null;
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
            var result = await controller.GetTeam(hackName, teamId, cancellationToken);
            // verify
            Mock.VerifyAll(hackathonManagement);
            hackathonManagement.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 404, string.Format(Resources.Hackathon_NotFound, hackName));
        }

        [Test]
        public async Task GetTeam_TeamNotFound()
        {
            // input
            string hackName = "Foo";
            string teamId = "tid";
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            TeamEntity teamEntity = null;
            CancellationToken cancellationToken = CancellationToken.None;
            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(hackathon);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("foo", "tid", cancellationToken))
                .ReturnsAsync(teamEntity);
            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                TeamManagement = teamManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.GetTeam(hackName, teamId, cancellationToken);
            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 404, Resources.Team_NotFound);
        }

        [Test]
        public async Task GetTeam_Succeeded()
        {
            // input
            string hackName = "Foo";
            string teamId = "tid";
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            TeamEntity teamEntity = new TeamEntity { CreatorId = "uid" };
            CancellationToken cancellationToken = CancellationToken.None;

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(hackathon);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("foo", "tid", cancellationToken))
                .ReturnsAsync(teamEntity);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                TeamManagement = teamManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.GetTeam(hackName, teamId, cancellationToken);
            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();

            Team output = AssertHelper.AssertOKResult<Team>(result);
            Assert.AreEqual("uid", output.creatorId);
        }

        [Test]
        public async Task CreateTeamMember_Create()
        {
            // input
            string hackName = "Foo";
            string teamId = "tid";
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            EnrollmentEntity enrollmentEntity = new EnrollmentEntity { Status = EnrollmentStatus.approved };
            TeamEntity teamEntity = new TeamEntity { CreatorId = "uid" };
            TeamMemberEntity memberEntity = new TeamMemberEntity { Description = "desc" };
            TeamMember request = new TeamMember();
            CancellationToken cancellationToken = CancellationToken.None;

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(hackathon);
            hackathonManagement.Setup(p => p.GetEnrollmentAsync("foo", "", cancellationToken))
                .ReturnsAsync(enrollmentEntity);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("foo", "tid", cancellationToken))
                .ReturnsAsync(teamEntity);
            teamManagement.Setup(t => t.GetTeamMemberAsync("tid", "", cancellationToken))
                .ReturnsAsync(default(TeamMemberEntity));
            teamManagement.Setup(t => t.CreateTeamMemberAsync(teamEntity, request, cancellationToken))
                .ReturnsAsync(memberEntity);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                TeamManagement = teamManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.CreateTeamMember(hackName, teamId, request, cancellationToken);
            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();

            TeamMember output = AssertHelper.AssertOKResult<TeamMember>(result);
            Assert.AreEqual("desc", output.description);
        }

        [Test]
        public async Task CreateTeamMember_Update()
        {
            // input
            string hackName = "Foo";
            string teamId = "tid";
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            EnrollmentEntity enrollmentEntity = new EnrollmentEntity { Status = EnrollmentStatus.approved };
            TeamEntity teamEntity = new TeamEntity { CreatorId = "uid" };
            TeamMemberEntity memberEntity = new TeamMemberEntity { Description = "desc" };
            TeamMember request = new TeamMember { };
            CancellationToken cancellationToken = CancellationToken.None;

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(hackathon);
            hackathonManagement.Setup(p => p.GetEnrollmentAsync("foo", "", cancellationToken))
                .ReturnsAsync(enrollmentEntity);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("foo", "tid", cancellationToken))
                .ReturnsAsync(teamEntity);
            teamManagement.Setup(t => t.GetTeamMemberAsync("tid", "", cancellationToken))
                .ReturnsAsync(memberEntity);
            teamManagement.Setup(t => t.UpdateTeamMemberAsync(memberEntity, request, cancellationToken))
                .ReturnsAsync(memberEntity);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                TeamManagement = teamManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.CreateTeamMember(hackName, teamId, request, cancellationToken);
            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();

            TeamMember output = AssertHelper.AssertOKResult<TeamMember>(result);
            Assert.AreEqual("desc", output.description);
        }

        [Test]
        public async Task UpdateTeamMember_TeamNotFound()
        {
            // input
            string hackName = "Foo";
            string teamId = "tid";
            string userId = "uid";
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            EnrollmentEntity enrollmentEntity = new EnrollmentEntity { Status = EnrollmentStatus.approved };
            TeamEntity teamEntity = null;
            TeamMemberEntity memberEntity = null;
            TeamMember request = new TeamMember { };
            CancellationToken cancellationToken = CancellationToken.None;

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(hackathon);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("foo", "tid", cancellationToken))
                .ReturnsAsync(teamEntity);
            teamManagement.Setup(t => t.GetTeamMemberAsync("tid", "uid", cancellationToken))
                .ReturnsAsync(memberEntity);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                TeamManagement = teamManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.UpdateTeamMember(hackName, teamId, userId, request, cancellationToken);
            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();

            AssertHelper.AssertObjectResult(result, 404, Resources.Team_NotFound);
        }

        [Test]
        public async Task UpdateTeamMember_TeamMemberNotFound()
        {
            // input
            string hackName = "Foo";
            string teamId = "tid";
            string userId = "uid";
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            EnrollmentEntity enrollmentEntity = new EnrollmentEntity { Status = EnrollmentStatus.approved };
            TeamEntity teamEntity = new TeamEntity { };
            TeamMemberEntity memberEntity = null;
            TeamMember request = new TeamMember { };
            CancellationToken cancellationToken = CancellationToken.None;

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(hackathon);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("foo", "tid", cancellationToken))
                .ReturnsAsync(teamEntity);
            teamManagement.Setup(t => t.GetTeamMemberAsync("tid", "uid", cancellationToken))
                .ReturnsAsync(memberEntity);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                TeamManagement = teamManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.UpdateTeamMember(hackName, teamId, userId, request, cancellationToken);
            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();

            AssertHelper.AssertObjectResult(result, 404, string.Format(Resources.TeamMember_NotFound, "uid", "tid"));
        }

        [Test]
        public async Task UpdateTeamMember_TeamMemberNotApproved()
        {
            // input
            string hackName = "Foo";
            string teamId = "tid";
            string userId = "uid";
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            EnrollmentEntity enrollmentEntity = new EnrollmentEntity { Status = EnrollmentStatus.approved };
            TeamEntity teamEntity = new TeamEntity { };
            TeamMemberEntity memberEntity = new TeamMemberEntity { };
            TeamMember request = new TeamMember { };
            var authResult = AuthorizationResult.Failed();
            CancellationToken cancellationToken = CancellationToken.None;

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(hackathon);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("foo", "tid", cancellationToken))
                .ReturnsAsync(teamEntity);
            teamManagement.Setup(t => t.GetTeamMemberAsync("tid", "uid", cancellationToken))
                .ReturnsAsync(memberEntity);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), teamEntity, AuthConstant.Policy.TeamMember))
                .ReturnsAsync(authResult);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                TeamManagement = teamManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
                AuthorizationService = authorizationService.Object,
            };
            var result = await controller.UpdateTeamMember(hackName, teamId, userId, request, cancellationToken);
            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement, authorizationService);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();

            AssertHelper.AssertObjectResult(result, 403, string.Format(Resources.TeamMember_AccessDenied, ""));
        }

        [Test]
        public async Task UpdateTeamMember_Updated()
        {
            // input
            string hackName = "Foo";
            string teamId = "tid";
            string userId = "uid";
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            EnrollmentEntity enrollmentEntity = new EnrollmentEntity { Status = EnrollmentStatus.approved };
            TeamEntity teamEntity = new TeamEntity { };
            TeamMemberEntity memberEntity = new TeamMemberEntity { Description = "desc1" };
            TeamMemberEntity memberEntityUpdated = new TeamMemberEntity { Description = "desc2" };
            TeamMember request = new TeamMember { };
            var authResult = AuthorizationResult.Success();
            CancellationToken cancellationToken = CancellationToken.None;

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(hackathon);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("foo", "tid", cancellationToken))
                .ReturnsAsync(teamEntity);
            teamManagement.Setup(t => t.GetTeamMemberAsync("tid", "uid", cancellationToken))
                .ReturnsAsync(memberEntity);
            teamManagement.Setup(t => t.UpdateTeamMemberAsync(memberEntity, request, cancellationToken))
                .ReturnsAsync(memberEntityUpdated);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), teamEntity, AuthConstant.Policy.TeamMember))
                .ReturnsAsync(authResult);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                TeamManagement = teamManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
                AuthorizationService = authorizationService.Object,
            };
            var result = await controller.UpdateTeamMember(hackName, teamId, userId, request, cancellationToken);
            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement, authorizationService);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();

            var resp = AssertHelper.AssertOKResult<TeamMember>(result);
            Assert.AreEqual("desc2", resp.description);
        }

        [Test]
        public async Task ApproveTeamMember_MemberNotFound()
        {
            // input
            string hackName = "Foo";
            string teamId = "tid";
            string userId = "uid";
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            EnrollmentEntity enrollmentEntity = new EnrollmentEntity { Status = EnrollmentStatus.approved };
            TeamEntity teamEntity = new TeamEntity { };
            TeamMemberEntity memberEntity = null;
            var authResult = AuthorizationResult.Success();
            CancellationToken cancellationToken = CancellationToken.None;

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(hackathon);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("foo", "tid", cancellationToken))
                .ReturnsAsync(teamEntity);
            teamManagement.Setup(t => t.GetTeamMemberAsync("tid", "uid", cancellationToken))
                .ReturnsAsync(memberEntity);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), teamEntity, AuthConstant.Policy.TeamAdministrator))
                .ReturnsAsync(authResult);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                TeamManagement = teamManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
                AuthorizationService = authorizationService.Object,
            };
            var result = await controller.ApproveTeamMember(hackName, teamId, userId, cancellationToken);
            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement, authorizationService);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();

            AssertHelper.AssertObjectResult(result, 404, string.Format(Resources.TeamMember_NotFound, "uid", "tid"));
        }

        [Test]
        public async Task ApproveTeamMember_Succeeded()
        {
            // input
            string hackName = "Foo";
            string teamId = "tid";
            string userId = "uid";
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            EnrollmentEntity enrollmentEntity = new EnrollmentEntity { Status = EnrollmentStatus.approved };
            TeamEntity teamEntity = new TeamEntity { };
            TeamMemberEntity memberEntity = new TeamMemberEntity();
            var authResult = AuthorizationResult.Success();
            CancellationToken cancellationToken = CancellationToken.None;

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(hackathon);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("foo", "tid", cancellationToken))
                .ReturnsAsync(teamEntity);
            teamManagement.Setup(t => t.GetTeamMemberAsync("tid", "uid", cancellationToken))
                .ReturnsAsync(memberEntity);
            teamManagement.Setup(t => t.UpdateTeamMemberStatusAsync(memberEntity, TeamMemberStatus.approved, cancellationToken))
                .Callback<TeamMemberEntity, TeamMemberStatus, CancellationToken>((m, s, c) =>
                {
                    m.Status = s;
                })
                .ReturnsAsync(memberEntity);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), teamEntity, AuthConstant.Policy.TeamAdministrator))
                .ReturnsAsync(authResult);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                TeamManagement = teamManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
                AuthorizationService = authorizationService.Object,
            };
            var result = await controller.ApproveTeamMember(hackName, teamId, userId, cancellationToken);
            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement, authorizationService);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();

            var resp = AssertHelper.AssertOKResult<TeamMember>(result);
            Assert.AreEqual(TeamMemberStatus.approved, resp.status);
        }

        [Test]
        public async Task LeaveTeam_NotMember()
        {
            // input
            string hackName = "Foo";
            string teamId = "tid";
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            TeamEntity teamEntity = new TeamEntity { };
            TeamMemberEntity memberEntity = null;
            CancellationToken cancellationToken = CancellationToken.None;

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(hackathon);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("foo", "tid", cancellationToken))
                .ReturnsAsync(teamEntity);
            teamManagement.Setup(t => t.GetTeamMemberAsync("tid", "", cancellationToken))
                .ReturnsAsync(memberEntity);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                TeamManagement = teamManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.LeaveTeam(hackName, teamId, cancellationToken);
            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();

            AssertHelper.AssertNoContentResult(result);
        }

        [Test]
        public async Task LeaveTeam_LastAdmin()
        {
            // input
            string hackName = "Foo";
            string teamId = "tid";
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            TeamEntity teamEntity = new TeamEntity { };
            TeamMemberEntity memberEntity = new TeamMemberEntity { };
            List<TeamMemberEntity> teamMembers = new List<TeamMemberEntity>
            {
                // admin
                new TeamMemberEntity
                {
                    PartitionKey = teamId,
                    RowKey = "",
                    Role = TeamMemberRole.Admin,
                    Status = TeamMemberStatus.approved
                },
                // other non-admin
                new TeamMemberEntity
                {
                    PartitionKey = teamId,
                    RowKey = "user2",
                    Role = TeamMemberRole.Member,
                    Status = TeamMemberStatus.approved
                },
                new TeamMemberEntity
                {
                    PartitionKey = teamId,
                    RowKey = "user2",
                    Role = TeamMemberRole.Admin,
                    Status = TeamMemberStatus.pendingApproval
                },
            };
            CancellationToken cancellationToken = CancellationToken.None;

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(hackathon);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("foo", "tid", cancellationToken))
                .ReturnsAsync(teamEntity);
            teamManagement.Setup(t => t.GetTeamMemberAsync("tid", "", cancellationToken))
                .ReturnsAsync(memberEntity);
            teamManagement.Setup(t => t.ListTeamMembersAsync("tid", cancellationToken))
                .ReturnsAsync(teamMembers);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                TeamManagement = teamManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.LeaveTeam(hackName, teamId, cancellationToken);
            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();

            AssertHelper.AssertObjectResult(result, 412, Resources.TeamMember_LastAdmin);
        }

        [Test]
        public async Task LeaveTeam_Succeeded()
        {
            // input
            string hackName = "Foo";
            string teamId = "tid";
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            TeamEntity teamEntity = new TeamEntity { };
            TeamMemberEntity memberEntity = new TeamMemberEntity { };
            List<TeamMemberEntity> teamMembers = new List<TeamMemberEntity>
            {
                // admin, not current user
                new TeamMemberEntity
                {
                    PartitionKey = teamId,
                    RowKey = "admin",
                    Role = TeamMemberRole.Admin,
                    Status = TeamMemberStatus.approved
                },
                // other non-admin
                new TeamMemberEntity
                {
                    PartitionKey = teamId,
                    RowKey = "user2",
                    Role = TeamMemberRole.Member,
                    Status = TeamMemberStatus.approved
                },
                new TeamMemberEntity
                {
                    PartitionKey = teamId,
                    RowKey = "user2",
                    Role = TeamMemberRole.Admin,
                    Status = TeamMemberStatus.pendingApproval
                },
            };
            CancellationToken cancellationToken = CancellationToken.None;

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(hackathon);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("foo", "tid", cancellationToken))
                .ReturnsAsync(teamEntity);
            teamManagement.Setup(t => t.GetTeamMemberAsync("tid", "", cancellationToken))
                .ReturnsAsync(memberEntity);
            teamManagement.Setup(t => t.ListTeamMembersAsync("tid", cancellationToken))
                .ReturnsAsync(teamMembers);
            teamManagement.Setup(t => t.DeleteTeamMemberAsync(memberEntity, cancellationToken));

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                TeamManagement = teamManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.LeaveTeam(hackName, teamId, cancellationToken);
            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();

            AssertHelper.AssertNoContentResult(result);
        }

        [Test]
        public async Task DeleteTeam_AlreadyDeleted()
        {
            // input
            string hackName = "Foo";
            string teamId = "tid";
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            TeamEntity teamEntity = null;
            CancellationToken cancellationToken = CancellationToken.None;

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(hackathon);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("foo", "tid", cancellationToken))
                .ReturnsAsync(teamEntity);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                TeamManagement = teamManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.DeleteTeam(hackName, teamId, cancellationToken);
            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();

            AssertHelper.AssertNoContentResult(result);
        }

        [Test]
        public async Task DeleteTeam_Succeeded()
        {
            // input
            string hackName = "Foo";
            string teamId = "tid";
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            TeamEntity teamEntity = new TeamEntity { };
            CancellationToken cancellationToken = CancellationToken.None;
            var authResult = AuthorizationResult.Success();

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(hackathon);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("foo", "tid", cancellationToken))
                .ReturnsAsync(teamEntity);
            teamManagement.Setup(t => t.DeleteTeamAsync(teamEntity, cancellationToken));
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), teamEntity, AuthConstant.Policy.TeamAdministrator))
                .ReturnsAsync(authResult);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                TeamManagement = teamManagement.Object,
                AuthorizationService = authorizationService.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.DeleteTeam(hackName, teamId, cancellationToken);
            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement, authorizationService);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();

            AssertHelper.AssertNoContentResult(result);
        }

    }
}
