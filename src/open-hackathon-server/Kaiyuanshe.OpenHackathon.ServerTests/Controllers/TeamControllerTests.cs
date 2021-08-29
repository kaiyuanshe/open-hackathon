using Kaiyuanshe.OpenHackathon.Server;
using Kaiyuanshe.OpenHackathon.Server.Auth;
using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Controllers;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.ResponseBuilder;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.AspNetCore.Authorization;
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
    public class TeamControllerTests
    {
        #region CreateTeam
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

            var enrollmentManagement = new Mock<IEnrollmentManagement>();
            enrollmentManagement.Setup(p => p.GetEnrollmentAsync("foo", "", cancellationToken)).ReturnsAsync(enrollment);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                EnrollmentManagement = enrollmentManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.CreateTeam(hackName, parameter, cancellationToken);

            // verify
            Mock.VerifyAll(hackathonManagement, enrollmentManagement);
            hackathonManagement.VerifyNoOtherCalls();
            enrollmentManagement.VerifyNoOtherCalls();

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
            var enrollmentManagement = new Mock<IEnrollmentManagement>();
            enrollmentManagement.Setup(p => p.GetEnrollmentAsync("foo", "", cancellationToken)).ReturnsAsync(enrollment);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                EnrollmentManagement = enrollmentManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.CreateTeam(hackName, parameter, cancellationToken);

            // verify
            Mock.VerifyAll(hackathonManagement, enrollmentManagement);
            hackathonManagement.VerifyNoOtherCalls();
            enrollmentManagement.VerifyNoOtherCalls();

            AssertHelper.AssertObjectResult(result, 412, Resources.Enrollment_NotApproved);
        }

        [Test]
        public async Task CreateTeam_NameTaken()
        {
            // input
            string hackName = "Foo";
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            EnrollmentEntity enrollment = new EnrollmentEntity { Status = EnrollmentStatus.approved };
            Team parameter = new Team { displayName = "dn" };
            var teamsByName = new List<TeamEntity> { new TeamEntity() };

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", default))
                .ReturnsAsync(hackathon);
            var enrollmentManagement = new Mock<IEnrollmentManagement>();
            enrollmentManagement.Setup(p => p.GetEnrollmentAsync("foo", "", default)).ReturnsAsync(enrollment);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByNameAsync("foo", "dn", default)).ReturnsAsync(teamsByName);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                EnrollmentManagement = enrollmentManagement.Object,
                TeamManagement = teamManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.CreateTeam(hackName, parameter, default);

            // verify
            Mock.VerifyAll(hackathonManagement, enrollmentManagement, teamManagement);
            hackathonManagement.VerifyNoOtherCalls();
            enrollmentManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();

            AssertHelper.AssertObjectResult(result, 412, string.Format(Resources.Team_NameTaken, "dn"));
        }

        [Test]
        public async Task CreateTeam_CreateSecond()
        {
            // input
            string hackName = "Foo";
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            EnrollmentEntity enrollment = new EnrollmentEntity { Status = EnrollmentStatus.approved };
            Team parameter = new Team { displayName = "dn" };
            var teamsByName = new List<TeamEntity>();
            TeamMemberEntity teamMember = new TeamMemberEntity();

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", default))
                .ReturnsAsync(hackathon);
            var enrollmentManagement = new Mock<IEnrollmentManagement>();
            enrollmentManagement.Setup(p => p.GetEnrollmentAsync("foo", "", default)).ReturnsAsync(enrollment);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByNameAsync("foo", "dn", default)).ReturnsAsync(teamsByName);
            teamManagement.Setup(t => t.GetTeamMemberAsync("foo", "", default)).ReturnsAsync(teamMember);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                EnrollmentManagement = enrollmentManagement.Object,
                TeamManagement = teamManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.CreateTeam(hackName, parameter, default);

            // verify
            Mock.VerifyAll(hackathonManagement, enrollmentManagement, teamManagement);
            hackathonManagement.VerifyNoOtherCalls();
            enrollmentManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();

            AssertHelper.AssertObjectResult(result, 412, Resources.Team_CreateSecond);
        }

        [Test]
        public async Task CreateTeam_Created()
        {
            // input
            string hackName = "Foo";
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            EnrollmentEntity enrollment = new EnrollmentEntity { Status = EnrollmentStatus.approved };
            Team parameter = new Team { displayName = "dn" };
            TeamEntity teamEntity = new TeamEntity { AutoApprove = true, CreatorId = "uid", PartitionKey = "pk", RowKey = "rk" };
            TeamMemberEntity teamMember = null;

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", default))
                .ReturnsAsync(hackathon);
            var enrollmentManagement = new Mock<IEnrollmentManagement>();
            enrollmentManagement.Setup(p => p.GetEnrollmentAsync("foo", "", default)).ReturnsAsync(enrollment);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByNameAsync("foo", "dn", default)).ReturnsAsync(new List<TeamEntity>());
            teamManagement.Setup(t => t.GetTeamMemberAsync("foo", "", default)).ReturnsAsync(teamMember);
            teamManagement.Setup(t => t.CreateTeamAsync(parameter, default)).ReturnsAsync(teamEntity);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                EnrollmentManagement = enrollmentManagement.Object,
                TeamManagement = teamManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
                ResponseBuilder = new DefaultResponseBuilder(),
            };
            var result = await controller.CreateTeam(hackName, parameter, default);

            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement, enrollmentManagement);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            enrollmentManagement.VerifyNoOtherCalls();

            Assert.AreEqual("foo", parameter.hackathonName);
            Assert.AreEqual("", parameter.creatorId);
            Team resp = AssertHelper.AssertOKResult<Team>(result);
            Assert.AreEqual(true, resp.autoApprove.Value);
            Assert.AreEqual("uid", resp.creatorId);
            Assert.AreEqual("pk", resp.hackathonName);
            Assert.AreEqual("rk", resp.id);
        }
        #endregion

        #region UpdateTeam
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
        public async Task UpdateTeam_TeamNameTaken()
        {
            // input
            string hackName = "Foo";
            string teamId = "tid";
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            Team parameter = new Team { displayName = "dn2" };
            TeamEntity teamEntity = new TeamEntity { DisplayName = "dn" };
            var teamByName = new List<TeamEntity> { teamEntity };
            var authResult = AuthorizationResult.Success();

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", default)).ReturnsAsync(hackathon);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("foo", "tid", default)).ReturnsAsync(teamEntity);
            teamManagement.Setup(t => t.GetTeamByNameAsync("foo", "dn2", default)).ReturnsAsync(teamByName);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), teamEntity, AuthConstant.Policy.TeamAdministrator)).ReturnsAsync(authResult);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                TeamManagement = teamManagement.Object,
                AuthorizationService = authorizationService.Object,
            };
            var result = await controller.UpdateTeam(hackName, teamId, parameter, default);
          
            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            AssertHelper.AssertObjectResult(result, 412, string.Format(Resources.Team_NameTaken, "dn2"));
        }

        [TestCase(null, false)] // not in request
        [TestCase("dn", false)] // not updated
        [TestCase("dn2", true)] // not taken
        public async Task UpdateTeam_Succeeded(string newDisplayName, bool checkName)
        {
            // input
            string hackName = "Foo";
            string teamId = "tid";
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            Team parameter = new Team { displayName = newDisplayName };
            TeamEntity teamEntity = new TeamEntity { DisplayName = "dn" };
            TeamEntity updated = new TeamEntity { Description = "updated", CreatorId = "uid" };
            var teamByName = new List<TeamEntity> { };
            UserInfo user = new UserInfo();
            var authResult = AuthorizationResult.Success();

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", default))
                .ReturnsAsync(hackathon);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("foo", "tid", default))
                .ReturnsAsync(teamEntity);
            if (checkName)
            {
                teamManagement.Setup(t => t.GetTeamByNameAsync("foo", "dn2", default)).ReturnsAsync(teamByName);
            }
            teamManagement.Setup(t => t.UpdateTeamAsync(parameter, teamEntity, default))
                .ReturnsAsync(updated);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), teamEntity, AuthConstant.Policy.TeamAdministrator))
                .ReturnsAsync(authResult);
            var userManagement = new Mock<IUserManagement>();
            userManagement.Setup(u => u.GetUserByIdAsync("uid", default))
                .ReturnsAsync(user);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                TeamManagement = teamManagement.Object,
                AuthorizationService = authorizationService.Object,
                UserManagement = userManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.UpdateTeam(hackName, teamId, parameter, default);
            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement, authorizationService, userManagement);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();
            userManagement.VerifyNoOtherCalls();

            Team output = AssertHelper.AssertOKResult<Team>(result);
            Assert.AreEqual("updated", output.description);
        }
        #endregion

        #region GetTeam
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
            UserInfo user = new UserInfo();
            CancellationToken cancellationToken = CancellationToken.None;

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(hackathon);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("foo", "tid", cancellationToken))
                .ReturnsAsync(teamEntity);
            var userManagement = new Mock<IUserManagement>();
            userManagement.Setup(u => u.GetUserByIdAsync("uid", cancellationToken))
                .ReturnsAsync(user);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                TeamManagement = teamManagement.Object,
                UserManagement = userManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.GetTeam(hackName, teamId, cancellationToken);
            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement, userManagement);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            userManagement.VerifyNoOtherCalls();

            Team output = AssertHelper.AssertOKResult<Team>(result);
            Assert.AreEqual("uid", output.creatorId);
        }
        #endregion

        #region ListTeams
        private static IEnumerable ListTeamsTestData()
        {
            // arg0: pagination
            // arg1: mocked TableCotinuationToken
            // arg2: expected options
            // arg3: expected nextlink

            // no pagination, no filter, no top
            yield return new TestCaseData(
                    new Pagination { },
                    null,
                    new TeamQueryOptions { },
                    null
                );

            // with pagination and filters
            yield return new TestCaseData(
                    new Pagination { top = 10, np = "np", nr = "nr" },
                    null,
                    new TeamQueryOptions
                    {
                        Top = 10,
                        TableContinuationToken = new TableContinuationToken
                        {
                            NextPartitionKey = "np",
                            NextRowKey = "nr"
                        },
                    },
                    null
                );

            // next link
            yield return new TestCaseData(
                    new Pagination { },
                    new TableContinuationToken
                    {
                        NextPartitionKey = "np",
                        NextRowKey = "nr"
                    },
                    new TeamQueryOptions { },
                    "&np=np&nr=nr"
                );
        }

        [Test, TestCaseSource(nameof(ListTeamsTestData))]
        public async Task ListTeams(
            Pagination pagination,
            TableContinuationToken continuationToken,
            TeamQueryOptions expectedOptions,
            string expectedLink)
        {
            // input
            var hackName = "Hack";
            var cancellationToken = CancellationToken.None;
            HackathonEntity hackathonEntity = new HackathonEntity();
            var teams = new List<TeamEntity>
            {
                new TeamEntity
                {
                    PartitionKey = "pk",
                    RowKey = "rk",
                    CreatorId = "uid",
                }
            };
            UserInfo user = new UserInfo();
            var segment = MockHelper.CreateTableQuerySegment(teams, continuationToken);

            // mock and capture
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", It.IsAny<CancellationToken>()))
                .ReturnsAsync(hackathonEntity);
            var teamManagement = new Mock<ITeamManagement>();
            TeamQueryOptions optionsCaptured = null;
            teamManagement.Setup(p => p.ListPaginatedTeamsAsync("hack", It.IsAny<TeamQueryOptions>(), cancellationToken))
                .Callback<string, TeamQueryOptions, CancellationToken>((n, o, t) =>
                {
                    optionsCaptured = o;
                })
                .ReturnsAsync(segment);
            var userManagement = new Mock<IUserManagement>();
            userManagement.Setup(u => u.GetUserByIdAsync("uid", cancellationToken))
                .ReturnsAsync(user);

            // run
            var controller = new TeamController
            {
                ResponseBuilder = new DefaultResponseBuilder(),
                HackathonManagement = hackathonManagement.Object,
                UserManagement = userManagement.Object,
                TeamManagement = teamManagement.Object,
            };
            var result = await controller.ListTeams(hackName, pagination, cancellationToken);

            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement, userManagement);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            userManagement.VerifyNoOtherCalls();

            var list = AssertHelper.AssertOKResult<TeamList>(result);
            Assert.AreEqual(expectedLink, list.nextLink);
            Assert.AreEqual(1, list.value.Length);
            Assert.AreEqual("pk", list.value[0].hackathonName);
            Assert.AreEqual("rk", list.value[0].id);
            Assert.AreEqual(expectedOptions.Top, optionsCaptured.Top);
            Assert.AreEqual(expectedOptions.TableContinuationToken?.NextPartitionKey, optionsCaptured.TableContinuationToken?.NextPartitionKey);
            Assert.AreEqual(expectedOptions.TableContinuationToken?.NextRowKey, optionsCaptured.TableContinuationToken?.NextRowKey);
        }

        #endregion

        #region JoinTeam
        [TestCase(true, TeamMemberStatus.approved)]
        [TestCase(false, TeamMemberStatus.pendingApproval)]
        public async Task JoinTeam_Create(bool autoApprove, TeamMemberStatus expectedStatus)
        {
            // input
            string hackName = "Foo";
            string teamId = "tid";
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            EnrollmentEntity enrollmentEntity = new EnrollmentEntity { Status = EnrollmentStatus.approved };
            TeamEntity teamEntity = new TeamEntity { CreatorId = "uid", AutoApprove = autoApprove };
            TeamMemberEntity memberEntity = new TeamMemberEntity { Description = "desc" };
            TeamMember request = new TeamMember { };
            CancellationToken cancellationToken = CancellationToken.None;
            UserInfo user = new UserInfo();

            // moq
            TeamMember captured = null;
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(hackathon);
            var enrollmentManagement = new Mock<IEnrollmentManagement>();
            enrollmentManagement.Setup(p => p.GetEnrollmentAsync("foo", "", cancellationToken))
                .ReturnsAsync(enrollmentEntity);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("foo", "tid", cancellationToken))
                .ReturnsAsync(teamEntity);
            teamManagement.Setup(t => t.GetTeamMemberAsync("foo", "", cancellationToken))
                .ReturnsAsync(default(TeamMemberEntity));
            teamManagement.Setup(t => t.CreateTeamMemberAsync(request, cancellationToken))
                .ReturnsAsync(memberEntity)
                .Callback<TeamMember, CancellationToken>((tm, c) => { captured = tm; });
            var userManagement = new Mock<IUserManagement>();
            userManagement.Setup(u => u.GetUserByIdAsync("", cancellationToken))
                .ReturnsAsync(user);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                TeamManagement = teamManagement.Object,
                EnrollmentManagement = enrollmentManagement.Object,
                UserManagement = userManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.JoinTeam(hackName, teamId, request, cancellationToken);
            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement, enrollmentManagement, userManagement);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            enrollmentManagement.VerifyNoOtherCalls();
            userManagement.VerifyNoOtherCalls();

            TeamMember output = AssertHelper.AssertOKResult<TeamMember>(result);
            Assert.AreEqual("desc", output.description);
            Assert.AreEqual(expectedStatus, captured.status);
        }

        [TestCase(true)]
        [TestCase(false)]
        public async Task JoinTeam_Update(bool autoApprove)
        {
            // input
            string hackName = "Foo";
            string teamId = "tid";
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            EnrollmentEntity enrollmentEntity = new EnrollmentEntity { Status = EnrollmentStatus.approved };
            TeamEntity teamEntity = new TeamEntity { CreatorId = "uid", AutoApprove = autoApprove };
            TeamMemberEntity memberEntity = new TeamMemberEntity { Description = "desc", Status = TeamMemberStatus.pendingApproval };
            TeamMember request = new TeamMember { };
            CancellationToken cancellationToken = CancellationToken.None;
            UserInfo user = new UserInfo();

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(hackathon);
            var enrollmentManagement = new Mock<IEnrollmentManagement>();
            enrollmentManagement.Setup(p => p.GetEnrollmentAsync("foo", "", cancellationToken))
                .ReturnsAsync(enrollmentEntity);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("foo", "tid", cancellationToken))
                .ReturnsAsync(teamEntity);
            teamManagement.Setup(t => t.GetTeamMemberAsync("foo", "", cancellationToken))
                .ReturnsAsync(memberEntity);
            teamManagement.Setup(t => t.UpdateTeamMemberAsync(memberEntity, request, cancellationToken))
                .ReturnsAsync(memberEntity);
            var userManagement = new Mock<IUserManagement>();
            userManagement.Setup(u => u.GetUserByIdAsync("", cancellationToken))
                .ReturnsAsync(user);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                UserManagement = userManagement.Object,
                EnrollmentManagement = enrollmentManagement.Object,
                TeamManagement = teamManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.JoinTeam(hackName, teamId, request, cancellationToken);
            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement, enrollmentManagement, userManagement);
            hackathonManagement.VerifyNoOtherCalls();
            userManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            enrollmentManagement.VerifyNoOtherCalls();

            TeamMember output = AssertHelper.AssertOKResult<TeamMember>(result);
            Assert.AreEqual("desc", output.description);
            Assert.AreEqual(TeamMemberStatus.pendingApproval, output.status); // status should NOT be updated
        }

        #endregion

        #region AddTeamMember
        [TestCase(true)]
        [TestCase(false)]
        public async Task AddTeamMember_Create(bool autoApprove)
        {
            // input
            string hackName = "Foo";
            string teamId = "tid";
            string userId = "uid";
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            EnrollmentEntity enrollmentEntity = new EnrollmentEntity { Status = EnrollmentStatus.approved };
            TeamEntity teamEntity = new TeamEntity { CreatorId = "uid", AutoApprove = autoApprove };
            TeamMemberEntity memberEntity = new TeamMemberEntity { Description = "desc" };
            TeamMember request = new TeamMember();
            var authResult = AuthorizationResult.Success();
            CancellationToken cancellationToken = CancellationToken.None;
            UserInfo user = new UserInfo();

            // moq
            TeamMember captured = null;
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(hackathon);
            var enrollmentManagement = new Mock<IEnrollmentManagement>();
            enrollmentManagement.Setup(p => p.GetEnrollmentAsync("foo", "uid", cancellationToken))
                .ReturnsAsync(enrollmentEntity);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("foo", "tid", cancellationToken))
                .ReturnsAsync(teamEntity);
            teamManagement.Setup(t => t.GetTeamMemberAsync("foo", "uid", cancellationToken))
                .ReturnsAsync(default(TeamMemberEntity));
            teamManagement.Setup(t => t.CreateTeamMemberAsync(request, cancellationToken))
                .ReturnsAsync(memberEntity)
                .Callback<TeamMember, CancellationToken>((tm, c) => { captured = tm; });
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), teamEntity, AuthConstant.Policy.TeamAdministrator))
                .ReturnsAsync(authResult);
            var userManagement = new Mock<IUserManagement>();
            userManagement.Setup(u => u.GetUserByIdAsync("uid", cancellationToken))
                .ReturnsAsync(user);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                EnrollmentManagement = enrollmentManagement.Object,
                TeamManagement = teamManagement.Object,
                UserManagement = userManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
                AuthorizationService = authorizationService.Object,
            };
            var result = await controller.AddTeamMember(hackName, teamId, userId, request, cancellationToken);
            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement, enrollmentManagement, userManagement);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            userManagement.VerifyNoOtherCalls();
            enrollmentManagement.VerifyNoOtherCalls();

            TeamMember output = AssertHelper.AssertOKResult<TeamMember>(result);
            Assert.AreEqual("desc", output.description);
            Assert.AreEqual(TeamMemberStatus.approved, captured.status); // alwasy Approved if add by admin no matter whether is autoApprove
        }

        [TestCase(true)]
        [TestCase(false)]
        public async Task AddTeamMember_Update(bool autoApprove)
        {
            // input
            string hackName = "Foo";
            string teamId = "tid";
            string userId = "uid";
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            EnrollmentEntity enrollmentEntity = new EnrollmentEntity { Status = EnrollmentStatus.approved };
            TeamEntity teamEntity = new TeamEntity { CreatorId = "uid", AutoApprove = autoApprove };
            TeamMemberEntity memberEntity = new TeamMemberEntity { Description = "desc" };
            TeamMember request = new TeamMember { };
            var authResult = AuthorizationResult.Success();
            CancellationToken cancellationToken = CancellationToken.None;
            UserInfo user = new UserInfo();

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(hackathon);
            var enrollmentManagement = new Mock<IEnrollmentManagement>();
            enrollmentManagement.Setup(p => p.GetEnrollmentAsync("foo", "uid", cancellationToken))
                .ReturnsAsync(enrollmentEntity);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("foo", "tid", cancellationToken))
                .ReturnsAsync(teamEntity);
            teamManagement.Setup(t => t.GetTeamMemberAsync("foo", "uid", cancellationToken))
                .ReturnsAsync(memberEntity);
            teamManagement.Setup(t => t.UpdateTeamMemberAsync(memberEntity, request, cancellationToken))
                .ReturnsAsync(memberEntity);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), teamEntity, AuthConstant.Policy.TeamAdministrator))
                .ReturnsAsync(authResult);
            var userManagement = new Mock<IUserManagement>();
            userManagement.Setup(u => u.GetUserByIdAsync("uid", cancellationToken))
                .ReturnsAsync(user);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                TeamManagement = teamManagement.Object,
                UserManagement = userManagement.Object,
                EnrollmentManagement = enrollmentManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
                AuthorizationService = authorizationService.Object,
            };
            var result = await controller.AddTeamMember(hackName, teamId, userId, request, cancellationToken);
            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement, enrollmentManagement, userManagement);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            enrollmentManagement.VerifyNoOtherCalls();
            userManagement.VerifyNoOtherCalls();

            TeamMember output = AssertHelper.AssertOKResult<TeamMember>(result);
            Assert.AreEqual("desc", output.description);
            Assert.AreEqual(TeamMemberStatus.pendingApproval, output.status); // status should NOT be updated
        }
        #endregion

        #region UpdateTeamMember
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
            teamManagement.Setup(t => t.GetTeamMemberAsync("foo", "uid", cancellationToken))
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
            teamManagement.Setup(t => t.GetTeamMemberAsync("foo", "uid", cancellationToken))
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
            teamManagement.Setup(t => t.GetTeamMemberAsync("foo", "uid", cancellationToken))
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
            UserInfo user = new UserInfo();

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(hackathon);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("foo", "tid", cancellationToken))
                .ReturnsAsync(teamEntity);
            teamManagement.Setup(t => t.GetTeamMemberAsync("foo", "uid", cancellationToken))
                .ReturnsAsync(memberEntity);
            teamManagement.Setup(t => t.UpdateTeamMemberAsync(memberEntity, request, cancellationToken))
                .ReturnsAsync(memberEntityUpdated);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), teamEntity, AuthConstant.Policy.TeamMember))
                .ReturnsAsync(authResult);
            var userManagement = new Mock<IUserManagement>();
            userManagement.Setup(u => u.GetUserByIdAsync("uid", cancellationToken))
                .ReturnsAsync(user);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                TeamManagement = teamManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
                UserManagement = userManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
                AuthorizationService = authorizationService.Object,
            };
            var result = await controller.UpdateTeamMember(hackName, teamId, userId, request, cancellationToken);
            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement, authorizationService, userManagement);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            userManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();

            var resp = AssertHelper.AssertOKResult<TeamMember>(result);
            Assert.AreEqual("desc2", resp.description);
        }

        #endregion

        #region ApproveTeamMember
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
            teamManagement.Setup(t => t.GetTeamMemberAsync("foo", "uid", cancellationToken))
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
            UserInfo user = new UserInfo();

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(hackathon);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("foo", "tid", cancellationToken))
                .ReturnsAsync(teamEntity);
            teamManagement.Setup(t => t.GetTeamMemberAsync("foo", "uid", cancellationToken))
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
            var userManagement = new Mock<IUserManagement>();
            userManagement.Setup(u => u.GetUserByIdAsync("uid", cancellationToken))
                .ReturnsAsync(user);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                TeamManagement = teamManagement.Object,
                UserManagement = userManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
                AuthorizationService = authorizationService.Object,
            };
            var result = await controller.ApproveTeamMember(hackName, teamId, userId, cancellationToken);
            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement, authorizationService, userManagement);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();
            userManagement.VerifyNoOtherCalls();

            var resp = AssertHelper.AssertOKResult<TeamMember>(result);
            Assert.AreEqual(TeamMemberStatus.approved, resp.status);
        }
        #endregion

        #region UpdateTeamMemberRole
        [TestCase(null, TeamMemberRole.Member)]
        [TestCase(TeamMemberRole.Admin, TeamMemberRole.Admin)]
        [TestCase(TeamMemberRole.Member, TeamMemberRole.Member)]
        public async Task UpdateTeamMemberRole_Succeeded(TeamMemberRole? requestedRole, TeamMemberRole expectedRole)
        {
            // input
            string hackName = "Foo";
            string teamId = "tid";
            string userId = "uid";
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            TeamEntity teamEntity = new TeamEntity { };
            TeamMemberEntity memberEntity = new TeamMemberEntity { Role = TeamMemberRole.Member };
            var authResult = AuthorizationResult.Success();
            CancellationToken cancellationToken = CancellationToken.None;
            var parameter = new TeamMember { role = requestedRole };
            UserInfo user = new UserInfo();

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(hackathon);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("foo", "tid", cancellationToken))
                .ReturnsAsync(teamEntity);
            teamManagement.Setup(t => t.GetTeamMemberAsync("foo", "uid", cancellationToken))
                .ReturnsAsync(memberEntity);
            teamManagement.Setup(t => t.UpdateTeamMemberRoleAsync(memberEntity, expectedRole, cancellationToken))
                .ReturnsAsync(memberEntity);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), teamEntity, AuthConstant.Policy.TeamAdministrator))
                .ReturnsAsync(authResult);
            var userManagement = new Mock<IUserManagement>();
            userManagement.Setup(u => u.GetUserByIdAsync("uid", cancellationToken))
                .ReturnsAsync(user);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                TeamManagement = teamManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
                UserManagement = userManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
                AuthorizationService = authorizationService.Object,
            };
            var result = await controller.UpdateTeamMemberRole(hackName, teamId, userId, parameter, cancellationToken);
            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement, authorizationService, userManagement);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            userManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();

            var resp = AssertHelper.AssertOKResult<TeamMember>(result);
        }
        #endregion

        #region LeaveTeam
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
            teamManagement.Setup(t => t.GetTeamMemberAsync("foo", "", cancellationToken))
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
            teamManagement.Setup(t => t.GetTeamMemberAsync("foo", "", cancellationToken))
                .ReturnsAsync(memberEntity);
            teamManagement.Setup(t => t.ListTeamMembersAsync("foo", "tid", cancellationToken))
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
            teamManagement.Setup(t => t.GetTeamMemberAsync("foo", "", cancellationToken))
                .ReturnsAsync(memberEntity);
            teamManagement.Setup(t => t.ListTeamMembersAsync("foo", "tid", cancellationToken))
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

        #endregion

        #region DeleteTeamMember
        [Test]
        public async Task DeleteTeamMember_Succeeded()
        {
            // input
            string hackName = "Foo";
            string teamId = "tid";
            string userId = "uid";
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
            var authResult = AuthorizationResult.Success();
            CancellationToken cancellationToken = CancellationToken.None;

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(hackathon);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("foo", "tid", cancellationToken))
                .ReturnsAsync(teamEntity);
            teamManagement.Setup(t => t.GetTeamMemberAsync("foo", "uid", cancellationToken))
                .ReturnsAsync(memberEntity);
            teamManagement.Setup(t => t.ListTeamMembersAsync("foo", "tid", cancellationToken))
                .ReturnsAsync(teamMembers);
            teamManagement.Setup(t => t.DeleteTeamMemberAsync(memberEntity, cancellationToken));
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), teamEntity, AuthConstant.Policy.TeamAdministrator))
                .ReturnsAsync(authResult);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                TeamManagement = teamManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
                AuthorizationService = authorizationService.Object,
            };
            var result = await controller.DeleteTeamMember(hackName, teamId, userId, cancellationToken);
            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement, authorizationService);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();

            AssertHelper.AssertNoContentResult(result);
        }
        #endregion

        #region DeleteTeam

        [Test]
        public async Task DeleteTeam_AlreadyDeleted()
        {
            // input
            string hackName = "Foo";
            string teamId = "tid";
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            TeamEntity teamEntity = null;

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", default))
                .ReturnsAsync(hackathon);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("foo", "tid", default))
                .ReturnsAsync(teamEntity);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                TeamManagement = teamManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.DeleteTeam(hackName, teamId, default);
            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();

            AssertHelper.AssertNoContentResult(result);
        }

        [Test]
        public async Task DeleteTeam_HasAssignment()
        {
            // input
            string hackName = "Foo";
            string teamId = "tid";
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            TeamEntity teamEntity = new TeamEntity { PartitionKey = "foo", RowKey = "rk" };
            var assignments = new List<AwardAssignmentEntity>
            {
                new AwardAssignmentEntity
                {
                    Description = "desc"
                }
            };
            var authResult = AuthorizationResult.Success();

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", default))
                .ReturnsAsync(hackathon);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("foo", "tid", default))
                .ReturnsAsync(teamEntity);
            var awardManagement = new Mock<IAwardManagement>();
            awardManagement.Setup(a => a.ListAssignmentsByTeamAsync("foo", "rk", default))
                .ReturnsAsync(assignments);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), teamEntity, AuthConstant.Policy.TeamAdministrator))
                .ReturnsAsync(authResult);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                AwardManagement = awardManagement.Object,
                TeamManagement = teamManagement.Object,
                AuthorizationService = authorizationService.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.DeleteTeam(hackName, teamId, default);
            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement, awardManagement, authorizationService);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            awardManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();

            AssertHelper.AssertObjectResult(result, 412, Resources.Team_HasAward);
        }

        [Test]
        public async Task DeleteTeam_HasRating()
        {
            // input
            string hackName = "Foo";
            string teamId = "tid";
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            TeamEntity teamEntity = new TeamEntity { PartitionKey = "foo", RowKey = "rk" };
            var assignments = new List<AwardAssignmentEntity>();
            var authResult = AuthorizationResult.Success();

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", default))
                .ReturnsAsync(hackathon);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("foo", "tid", default))
                .ReturnsAsync(teamEntity);
            var awardManagement = new Mock<IAwardManagement>();
            awardManagement.Setup(a => a.ListAssignmentsByTeamAsync("foo", "rk", default))
                .ReturnsAsync(assignments);
            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), teamEntity, AuthConstant.Policy.TeamAdministrator))
                .ReturnsAsync(authResult);
            var ratingManagement = new Mock<IRatingManagement>();
            ratingManagement.Setup(j => j.IsRatingCountGreaterThanZero(
                "foo",
                It.Is<RatingQueryOptions>(o => o.RatingKindId == null && o.JudgeId == null && o.TeamId == "rk"),
                default)).ReturnsAsync(true);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                AwardManagement = awardManagement.Object,
                TeamManagement = teamManagement.Object,
                AuthorizationService = authorizationService.Object,
                RatingManagement = ratingManagement.Object,
            };
            var result = await controller.DeleteTeam(hackName, teamId, default);
            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement, ratingManagement, awardManagement, authorizationService);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            awardManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();
            ratingManagement.VerifyNoOtherCalls();

            AssertHelper.AssertObjectResult(result, 412, string.Format(Resources.Rating_HasRating, nameof(Team)));
        }

        [Test]
        public async Task DeleteTeam_Succeeded()
        {
            // input
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            TeamEntity teamEntity = new TeamEntity { PartitionKey = "foo", RowKey = "tid" };
            var authResult = AuthorizationResult.Success();
            var assignments = new List<AwardAssignmentEntity>();
            var members = new List<TeamMemberEntity>
            {
                new TeamMemberEntity { PartitionKey="foo" },
            };

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", default)).ReturnsAsync(hackathon);

            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("foo", "tid", default)).ReturnsAsync(teamEntity);
            teamManagement.Setup(t => t.ListTeamMembersAsync("foo", "tid", default)).ReturnsAsync(members);
            teamManagement.Setup(t => t.DeleteTeamMemberAsync(It.Is<TeamMemberEntity>(m => m.HackathonName == "foo"), default));
            teamManagement.Setup(t => t.DeleteTeamAsync(teamEntity, default));

            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), teamEntity, AuthConstant.Policy.TeamAdministrator))
                .ReturnsAsync(authResult);
            var awardManagement = new Mock<IAwardManagement>();
            awardManagement.Setup(a => a.ListAssignmentsByTeamAsync("foo", "tid", default))
                .ReturnsAsync(assignments);
            var ratingManagement = new Mock<IRatingManagement>();
            ratingManagement.Setup(j => j.IsRatingCountGreaterThanZero(
                "foo",
                It.Is<RatingQueryOptions>(o => o.RatingKindId == null && o.JudgeId == null && o.TeamId == "tid"),
                default)).ReturnsAsync(false);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                TeamManagement = teamManagement.Object,
                AuthorizationService = authorizationService.Object,
                AwardManagement = awardManagement.Object,
                RatingManagement = ratingManagement.Object,
            };
            var result = await controller.DeleteTeam("Foo", "tid", default);
            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement, ratingManagement, authorizationService, awardManagement);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();
            awardManagement.VerifyNoOtherCalls();
            ratingManagement.VerifyNoOtherCalls();

            AssertHelper.AssertNoContentResult(result);
        }
        #endregion

        #region GetTeamMember
        [Test]
        public async Task GetTeamMember_Succeeded()
        {
            // input
            string hackName = "Foo";
            string teamId = "tid";
            string userId = "uid";
            HackathonEntity hackathon = new HackathonEntity { };
            TeamEntity teamEntity = new TeamEntity { };
            TeamMemberEntity teamMemberEntity = new TeamMemberEntity { Description = "desc" };
            CancellationToken cancellationToken = CancellationToken.None;
            UserInfo user = new UserInfo();

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("foo", cancellationToken))
                .ReturnsAsync(hackathon);
            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("foo", "tid", cancellationToken))
                .ReturnsAsync(teamEntity);
            teamManagement.Setup(t => t.GetTeamMemberAsync("foo", "uid", cancellationToken))
                .ReturnsAsync(teamMemberEntity);
            var userManagement = new Mock<IUserManagement>();
            userManagement.Setup(u => u.GetUserByIdAsync("uid", cancellationToken))
                .ReturnsAsync(user);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                TeamManagement = teamManagement.Object,
                UserManagement = userManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
                ResponseBuilder = new DefaultResponseBuilder(),
            };
            var result = await controller.GetTeamMember(hackName, teamId, userId, cancellationToken);
            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement, userManagement);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            userManagement.VerifyNoOtherCalls();

            var resp = AssertHelper.AssertOKResult<TeamMember>(result);
            Assert.AreEqual("desc", resp.description);
        }
        #endregion

        #region ListMembers
        private static IEnumerable ListMembersTestData()
        {
            // arg0: pagination
            // arg1: status
            // arg2: role
            // arg3: mocked TableCotinuationToken
            // arg4: expected options
            // arg5: expected nextlink

            // no pagination, no filter, no top
            yield return new TestCaseData(
                    new Pagination { },
                    null,
                    null,
                    null,
                    new TeamMemberQueryOptions { },
                    null
                );

            // with pagination and filters
            yield return new TestCaseData(
                    new Pagination { top = 10, np = "np", nr = "nr" },
                    TeamMemberStatus.approved,
                    TeamMemberRole.Admin,
                    null,
                    new TeamMemberQueryOptions
                    {
                        Top = 10,
                        TableContinuationToken = new TableContinuationToken
                        {
                            NextPartitionKey = "np",
                            NextRowKey = "nr"
                        },
                        Status = TeamMemberStatus.approved,
                        Role = TeamMemberRole.Admin
                    },
                    null
                );

            // next link
            yield return new TestCaseData(
                    new Pagination { },
                    null,
                    null,
                    new TableContinuationToken
                    {
                        NextPartitionKey = "np",
                        NextRowKey = "nr"
                    },
                    new TeamMemberQueryOptions { },
                    "&np=np&nr=nr"
                );
        }

        [Test, TestCaseSource(nameof(ListMembersTestData))]
        public async Task ListMembers_Succeed(
            Pagination pagination,
            TeamMemberStatus? status,
            TeamMemberRole? role,
            TableContinuationToken continuationToken,
            TeamMemberQueryOptions expectedOptions,
            string expectedLink)
        {
            // input
            var hackName = "Hack";
            var teamId = "tid";
            var cancellationToken = CancellationToken.None;
            HackathonEntity hackathonEntity = new HackathonEntity();
            TeamEntity teamEntity = new TeamEntity();
            var members = new List<TeamMemberEntity>
            {
                new TeamMemberEntity
                {
                    PartitionKey = "pk",
                    RowKey = "rk",
                    TeamId = "tid",
                    Status = TeamMemberStatus.approved,
                    Role = TeamMemberRole.Admin,
                }
            };
            var segment = MockHelper.CreateTableQuerySegment(members, continuationToken);
            UserInfo user = new UserInfo { Company = "company" };

            // mock and capture
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", It.IsAny<CancellationToken>()))
                .ReturnsAsync(hackathonEntity);
            var teamManagement = new Mock<ITeamManagement>();
            TeamMemberQueryOptions optionsCaptured = null;
            teamManagement.Setup(p => p.GetTeamByIdAsync("hack", "tid", cancellationToken))
                .ReturnsAsync(teamEntity);
            teamManagement.Setup(p => p.ListPaginatedTeamMembersAsync("hack", "tid", It.IsAny<TeamMemberQueryOptions>(), cancellationToken))
                .Callback<string, string, TeamMemberQueryOptions, CancellationToken>((h, n, o, t) =>
                {
                    optionsCaptured = o;
                })
                .ReturnsAsync(segment);
            var userManagement = new Mock<IUserManagement>();
            userManagement.Setup(u => u.GetUserByIdAsync("rk", cancellationToken))
                .ReturnsAsync(user);

            // run
            var controller = new TeamController
            {
                ResponseBuilder = new DefaultResponseBuilder(),
                UserManagement = userManagement.Object,
                HackathonManagement = hackathonManagement.Object,
                TeamManagement = teamManagement.Object,
            };
            var result = await controller.ListMembers(hackName, teamId, pagination, role, status, cancellationToken);

            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement, userManagement);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            userManagement.VerifyNoOtherCalls();

            var list = AssertHelper.AssertOKResult<TeamMemberList>(result);
            Assert.AreEqual(expectedLink, list.nextLink);
            Assert.AreEqual(1, list.value.Length);
            Assert.AreEqual("tid", list.value[0].teamId);
            Assert.AreEqual("rk", list.value[0].userId);
            Assert.AreEqual(TeamMemberStatus.approved, list.value[0].status);
            Assert.AreEqual(TeamMemberRole.Admin, list.value[0].role);
            Assert.AreEqual("company", list.value[0].user.Company);

            Assert.AreEqual(expectedOptions.Status, optionsCaptured.Status);
            Assert.AreEqual(expectedOptions.Role, optionsCaptured.Role);
            Assert.AreEqual(expectedOptions.Top, optionsCaptured.Top);
            Assert.AreEqual(expectedOptions.TableContinuationToken?.NextPartitionKey, optionsCaptured.TableContinuationToken?.NextPartitionKey);
            Assert.AreEqual(expectedOptions.TableContinuationToken?.NextRowKey, optionsCaptured.TableContinuationToken?.NextRowKey);
        }
        #endregion

        #region ListAssignmentsByTeam
        private static IEnumerable ListAssignmentsByTeamTestData()
        {
            // arg0: pagination
            // arg1: next TableCotinuationToken
            // arg2: expected nextlink

            // no pagination, no filter, no top
            yield return new TestCaseData(
                    new Pagination { },
                    null,
                    null
                );

            // with pagination and filters
            yield return new TestCaseData(
                    new Pagination { top = 10, np = "np", nr = "nr" },
                    null,
                    null
                );

            // next link
            yield return new TestCaseData(
                    new Pagination { },
                    new TableContinuationToken
                    {
                        NextPartitionKey = "np",
                        NextRowKey = "nr"
                    },
                    "&np=np&nr=nr"
                );

            // next link with top
            yield return new TestCaseData(
                    new Pagination { top = 10, np = "np", nr = "nr" },
                    new TableContinuationToken
                    {
                        NextPartitionKey = "np2",
                        NextRowKey = "nr2"
                    },
                    "&top=10&np=np2&nr=nr2"
                );
        }

        [Test, TestCaseSource(nameof(ListAssignmentsByTeamTestData))]
        public async Task ListAssignmentsByTeam(
            Pagination pagination,
            TableContinuationToken next,
            string expectedLink)
        {
            // input
            HackathonEntity hackathon = new HackathonEntity();
            var assignments = new List<AwardAssignmentEntity>
            {
                new AwardAssignmentEntity
                {
                    PartitionKey = "pk",
                    RowKey = "rk",
                }
            };
            TeamEntity team = new TeamEntity { CreatorId = "creator" };
            var creator = new UserInfo { LastLogin = "2020" };

            // mock and capture
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);

            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync(It.IsAny<string>(), It.IsAny<string>(), default)).ReturnsAsync(team);

            var awardManagement = new Mock<IAwardManagement>();
            awardManagement.Setup(p => p.ListPaginatedAssignmentsAsync("hack", It.Is<AwardAssignmentQueryOptions>(o => o.QueryType == AwardAssignmentQueryType.Team), default))
                .Callback<string, AwardAssignmentQueryOptions, CancellationToken>((n, o, t) =>
                {
                    o.Next = next;
                })
                .ReturnsAsync(assignments);

            var userManagement = new Mock<IUserManagement>();
            userManagement.Setup(u => u.GetUserByIdAsync("creator", default)).ReturnsAsync(creator);

            // run
            var controller = new TeamController
            {
                ResponseBuilder = new DefaultResponseBuilder(),
                HackathonManagement = hackathonManagement.Object,
                AwardManagement = awardManagement.Object,
                TeamManagement = teamManagement.Object,
                UserManagement = userManagement.Object,
            };
            var result = await controller.ListAssignmentsByTeam("Hack", "awardId", pagination, default);

            // verify
            Mock.VerifyAll(hackathonManagement, awardManagement, teamManagement, userManagement);
            hackathonManagement.VerifyNoOtherCalls();
            awardManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            userManagement.VerifyNoOtherCalls();

            var list = AssertHelper.AssertOKResult<AwardAssignmentList>(result);
            Assert.AreEqual(expectedLink, list.nextLink);
            Assert.AreEqual(1, list.value.Length);
            Assert.AreEqual("pk", list.value[0].hackathonName);
            Assert.AreEqual("rk", list.value[0].assignmentId);
            Assert.AreEqual("2020", list.value[0].team.creator.LastLogin);
        }
        #endregion

        #region CreateTeamWork
        [Test]
        public async Task CreateTeamWork_TooMany()
        {
            // input
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            TeamEntity teamEntity = new TeamEntity { };
            TeamMemberEntity memberEntity = new TeamMemberEntity { };
            TeamWork request = new TeamWork { };
            TeamWorkEntity teamWorkEntity = new TeamWorkEntity { Description = "desc" };
            var authResult = AuthorizationResult.Success();

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);

            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("hack", "teamId", default)).ReturnsAsync(teamEntity);
            teamManagement.Setup(t => t.GetTeamMemberAsync("hack", It.IsAny<string>(), default)).ReturnsAsync(memberEntity);

            var workManagement = new Mock<IWorkManagement>();
            workManagement.Setup(w => w.CanCreateTeamWorkAsync("hack", "teamId", default)).ReturnsAsync(false);

            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), teamEntity, AuthConstant.Policy.TeamMember))
                .ReturnsAsync(authResult);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                TeamManagement = teamManagement.Object,
                WorkManagement = workManagement.Object,
                AuthorizationService = authorizationService.Object,
            };
            var result = await controller.CreateTeamWork("Hack", "teamId", request, default);

            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement, workManagement, authorizationService);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            workManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();

            AssertHelper.AssertObjectResult(result, 412, Resources.TeamWork_TooMany);
        }

        [Test]
        public async Task CreateTeamWork()
        {
            // input
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            TeamEntity teamEntity = new TeamEntity { };
            TeamMemberEntity memberEntity = new TeamMemberEntity { };
            TeamWork request = new TeamWork { };
            TeamWorkEntity teamWorkEntity = new TeamWorkEntity { Description = "desc" };
            var authResult = AuthorizationResult.Success();

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);

            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("hack", "teamId", default)).ReturnsAsync(teamEntity);
            teamManagement.Setup(t => t.GetTeamMemberAsync("hack", It.IsAny<string>(), default)).ReturnsAsync(memberEntity);

            var workManagement = new Mock<IWorkManagement>();
            workManagement.Setup(w => w.CreateTeamWorkAsync(It.Is<TeamWork>(work => work.hackathonName == "hack" && work.teamId == "teamId"), default)).ReturnsAsync(teamWorkEntity);
            workManagement.Setup(w => w.CanCreateTeamWorkAsync("hack", "teamId", default)).ReturnsAsync(true);

            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), teamEntity, AuthConstant.Policy.TeamMember))
                .ReturnsAsync(authResult);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                TeamManagement = teamManagement.Object,
                WorkManagement = workManagement.Object,
                AuthorizationService = authorizationService.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.CreateTeamWork("Hack", "teamId", request, default);

            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement, workManagement, authorizationService);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            workManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();

            TeamWork output = AssertHelper.AssertOKResult<TeamWork>(result);
            Assert.AreEqual("desc", output.description);
        }
        #endregion

        #region UpdateTeamWork
        [Test]
        public async Task UpdateTeamWork_NotFound()
        {
            // input
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            TeamEntity teamEntity = new TeamEntity { };
            TeamMemberEntity memberEntity = new TeamMemberEntity { };
            TeamWork request = new TeamWork { };
            TeamWorkEntity teamWorkEntity = null;
            var authResult = AuthorizationResult.Success();

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);

            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("hack", "teamId", default)).ReturnsAsync(teamEntity);
            teamManagement.Setup(t => t.GetTeamMemberAsync("hack", It.IsAny<string>(), default)).ReturnsAsync(memberEntity);

            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), teamEntity, AuthConstant.Policy.TeamMember))
                .ReturnsAsync(authResult);

            var workManagement = new Mock<IWorkManagement>();
            workManagement.Setup(w => w.GetTeamWorkAsync("hack", "workId", default)).ReturnsAsync(teamWorkEntity);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                TeamManagement = teamManagement.Object,
                WorkManagement = workManagement.Object,
                AuthorizationService = authorizationService.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.UpdateTeamWork("Hack", "teamId", "workId", request, default);

            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement, workManagement, authorizationService);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            workManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();

            AssertHelper.AssertObjectResult(result, 404, Resources.TeamWork_NotFound);
        }

        [Test]
        public async Task UpdateTeamWork_Succeeded()
        {
            // input
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            TeamEntity teamEntity = new TeamEntity { };
            TeamMemberEntity memberEntity = new TeamMemberEntity { };
            TeamWork request = new TeamWork { };
            TeamWorkEntity teamWorkEntity = new TeamWorkEntity { Description = "desc" };
            var authResult = AuthorizationResult.Success();

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);

            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("hack", "teamId", default)).ReturnsAsync(teamEntity);
            teamManagement.Setup(t => t.GetTeamMemberAsync("hack", It.IsAny<string>(), default)).ReturnsAsync(memberEntity);

            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), teamEntity, AuthConstant.Policy.TeamMember))
                .ReturnsAsync(authResult);

            var workManagement = new Mock<IWorkManagement>();
            workManagement.Setup(w => w.GetTeamWorkAsync("hack", "workId", default)).ReturnsAsync(teamWorkEntity);
            workManagement.Setup(w => w.UpdateTeamWorkAsync(It.IsAny<TeamWorkEntity>(), request, default)).ReturnsAsync(teamWorkEntity);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                TeamManagement = teamManagement.Object,
                WorkManagement = workManagement.Object,
                AuthorizationService = authorizationService.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.UpdateTeamWork("Hack", "teamId", "workId", request, default);

            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement, workManagement, authorizationService);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            workManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();

            TeamWork output = AssertHelper.AssertOKResult<TeamWork>(result);
            Assert.AreEqual("desc", output.description);
        }
        #endregion

        #region GetTeamWork
        [Test]
        public async Task GetTeamWork_NotFound()
        {
            // input
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            TeamEntity teamEntity = new TeamEntity { };
            TeamWorkEntity teamWorkEntity = null;

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);

            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("hack", "teamId", default)).ReturnsAsync(teamEntity);

            var workManagement = new Mock<IWorkManagement>();
            workManagement.Setup(w => w.GetTeamWorkAsync("hack", "workId", default)).ReturnsAsync(teamWorkEntity);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                TeamManagement = teamManagement.Object,
                WorkManagement = workManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.GetTeamWork("Hack", "teamId", "workId", default);

            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement, workManagement);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            workManagement.VerifyNoOtherCalls();

            AssertHelper.AssertObjectResult(result, 404, Resources.TeamWork_NotFound);
        }

        [Test]
        public async Task GetTeamWork_Success()
        {
            // input
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            TeamEntity teamEntity = new TeamEntity { };
            TeamWorkEntity teamWorkEntity = new TeamWorkEntity { Title = "title" };

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);

            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("hack", "teamId", default)).ReturnsAsync(teamEntity);

            var workManagement = new Mock<IWorkManagement>();
            workManagement.Setup(w => w.GetTeamWorkAsync("hack", "workId", default)).ReturnsAsync(teamWorkEntity);

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                TeamManagement = teamManagement.Object,
                WorkManagement = workManagement.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
            };
            var result = await controller.GetTeamWork("Hack", "teamId", "workId", default);

            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement, workManagement);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            workManagement.VerifyNoOtherCalls();

            TeamWork teamWork = AssertHelper.AssertOKResult<TeamWork>(result);
            Assert.AreEqual("title", teamWork.title);
        }
        #endregion

        #region ListWorksByTeam
        private static IEnumerable ListWorksByTeamTestData()
        {
            // arg0: pagination
            // arg1: next TableCotinuationToken
            // arg2: expected nextlink

            // no pagination, no filter, no top
            yield return new TestCaseData(
                    new Pagination { },
                    null,
                    null
                );

            // with pagination and filters
            yield return new TestCaseData(
                    new Pagination { top = 10, np = "np", nr = "nr" },
                    null,
                    null
                );

            // next link
            yield return new TestCaseData(
                    new Pagination { },
                    new TableContinuationToken
                    {
                        NextPartitionKey = "np",
                        NextRowKey = "nr"
                    },
                    "&np=np&nr=nr"
                );

            // next link with top
            yield return new TestCaseData(
                    new Pagination { top = 10, np = "np", nr = "nr" },
                    new TableContinuationToken
                    {
                        NextPartitionKey = "np2",
                        NextRowKey = "nr2"
                    },
                    "&top=10&np=np2&nr=nr2"
                );
        }

        [Test, TestCaseSource(nameof(ListWorksByTeamTestData))]
        public async Task ListWorksByTeam(
            Pagination pagination,
            TableContinuationToken next,
            string expectedLink)
        {
            // input
            HackathonEntity hackathon = new HackathonEntity();
            var teamWorks = new List<TeamWorkEntity>
            {
                new TeamWorkEntity
                {
                    PartitionKey = "pk",
                    RowKey = "rk",
                }
            };
            TeamEntity team = new TeamEntity { };

            // mock and capture
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);

            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync(It.IsAny<string>(), It.IsAny<string>(), default)).ReturnsAsync(team);

            var workManagement = new Mock<IWorkManagement>();
            workManagement.Setup(p => p.ListPaginatedWorksAsync("hack", "tid", It.IsAny<TeamWorkQueryOptions>(), default))
                .Callback<string, string, TeamWorkQueryOptions, CancellationToken>((h, t, o, c) =>
                {
                    o.Next = next;
                })
                .ReturnsAsync(teamWorks);

            // run
            var controller = new TeamController
            {
                ResponseBuilder = new DefaultResponseBuilder(),
                HackathonManagement = hackathonManagement.Object,
                WorkManagement = workManagement.Object,
                TeamManagement = teamManagement.Object,
            };
            var result = await controller.ListWorksByTeam("Hack", "tid", pagination, default);

            // verify
            Mock.VerifyAll(hackathonManagement, workManagement, teamManagement);
            hackathonManagement.VerifyNoOtherCalls();
            workManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();

            var list = AssertHelper.AssertOKResult<TeamWorkList>(result);
            Assert.AreEqual(expectedLink, list.nextLink);
            Assert.AreEqual(1, list.value.Length);
            Assert.AreEqual("pk", list.value[0].hackathonName);
            Assert.AreEqual("rk", list.value[0].id);
        }
        #endregion

        #region DeleteTeamWork
        [TestCase(true)]
        [TestCase(false)]
        public async Task DeleteTeamWork(bool firstTime)
        {
            // input
            HackathonEntity hackathon = new HackathonEntity { Status = HackathonStatus.online };
            TeamEntity teamEntity = new TeamEntity { };
            TeamMemberEntity memberEntity = new TeamMemberEntity { };
            TeamWorkEntity teamWorkEntity = firstTime ? new TeamWorkEntity() : null;
            var authResult = AuthorizationResult.Success();

            // moq
            var hackathonManagement = new Mock<IHackathonManagement>();
            hackathonManagement.Setup(p => p.GetHackathonEntityByNameAsync("hack", default)).ReturnsAsync(hackathon);

            var teamManagement = new Mock<ITeamManagement>();
            teamManagement.Setup(t => t.GetTeamByIdAsync("hack", "teamId", default)).ReturnsAsync(teamEntity);
            teamManagement.Setup(t => t.GetTeamMemberAsync("hack", It.IsAny<string>(), default)).ReturnsAsync(memberEntity);

            var authorizationService = new Mock<IAuthorizationService>();
            authorizationService.Setup(m => m.AuthorizeAsync(It.IsAny<ClaimsPrincipal>(), teamEntity, AuthConstant.Policy.TeamMember))
                .ReturnsAsync(authResult);

            var workManagement = new Mock<IWorkManagement>();
            workManagement.Setup(w => w.GetTeamWorkAsync("hack", "workId", default)).ReturnsAsync(teamWorkEntity);
            if (firstTime)
            {
                workManagement.Setup(w => w.DeleteTeamWorkAsync("hack", "workId", default));
            }

            // run
            var controller = new TeamController
            {
                HackathonManagement = hackathonManagement.Object,
                TeamManagement = teamManagement.Object,
                WorkManagement = workManagement.Object,
                AuthorizationService = authorizationService.Object,
            };
            var result = await controller.DeleteTeamWork("Hack", "teamId", "workId", default);

            // verify
            Mock.VerifyAll(hackathonManagement, teamManagement, workManagement, authorizationService);
            hackathonManagement.VerifyNoOtherCalls();
            teamManagement.VerifyNoOtherCalls();
            workManagement.VerifyNoOtherCalls();
            authorizationService.VerifyNoOtherCalls();

            AssertHelper.AssertNoContentResult(result);
        }
        #endregion
    }
}