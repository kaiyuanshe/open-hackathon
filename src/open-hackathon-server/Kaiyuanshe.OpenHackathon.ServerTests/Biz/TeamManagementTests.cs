using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Cache;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Storage;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Kaiyuanshe.OpenHackathon.Server.Storage.Tables;
using Microsoft.Extensions.Logging;
using Microsoft.WindowsAzure.Storage.Table;
using Moq;
using NUnit.Framework;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Biz
{
    [TestFixture]
    public class TeamManagementTests
    {
        #region CreateTeamAsync
        [TestCase(null, "uid")]
        [TestCase("", "uid")]
        [TestCase(" ", "uid")]
        [TestCase("foo", null)]
        [TestCase("foo", "")]
        [TestCase("foo", " ")]
        public async Task CreateTeamAsync_Null(string hackathonName, string userId)
        {
            var request = new Team { hackathonName = hackathonName, creatorId = userId };
            var cancellationToken = CancellationToken.None;
            var logger = new Mock<ILogger<TeamManagement>>();
            var teamManagement = new TeamManagement(logger.Object);
            Assert.IsNull(await teamManagement.CreateTeamAsync(request, cancellationToken));
            Mock.VerifyAll(logger);
        }

        [Test]
        public async Task CreateTeamAsync_Succeed()
        {
            var request = new Team
            {
                hackathonName = "hack",
                creatorId = "uid",
                description = "desc",
                autoApprove = false,
                displayName = "dp",
            };
            var cancellationToken = CancellationToken.None;
            TeamMemberEntity teamMember = null;

            var logger = new Mock<ILogger<TeamManagement>>();
            var teamTable = new Mock<ITeamTable>();
            teamTable.Setup(p => p.InsertAsync(It.IsAny<TeamEntity>(), cancellationToken));
            var teamMemberTable = new Mock<ITeamMemberTable>();
            teamMemberTable.Setup(p => p.InsertAsync(It.IsAny<TeamMemberEntity>(), cancellationToken))
                .Callback<TeamMemberEntity, CancellationToken>((t, c) => { teamMember = t; });
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.TeamTable).Returns(teamTable.Object);
            storageContext.SetupGet(p => p.TeamMemberTable).Returns(teamMemberTable.Object);

            var teamManagement = new TeamManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
            };
            var result = await teamManagement.CreateTeamAsync(request, cancellationToken);

            Mock.VerifyAll(logger, teamTable, teamMemberTable, storageContext);
            Assert.IsNotNull(result);
            Assert.AreEqual(false, result.AutoApprove);
            Assert.AreEqual("uid", result.CreatorId);
            Assert.AreEqual("desc", result.Description);
            Assert.AreEqual("dp", result.DisplayName);
            Assert.AreEqual("hack", result.HackathonName);
            Assert.IsNotNull(result.Id);
            Assert.AreEqual(1, result.MembersCount);

            Assert.IsNotNull(teamMember);
            Assert.AreEqual("hack", teamMember.HackathonName);
            Assert.AreEqual("hack", teamMember.PartitionKey);
            Assert.AreEqual(TeamMemberRole.Admin, teamMember.Role);
            Assert.AreEqual(TeamMemberStatus.approved, teamMember.Status);
            Assert.AreEqual(result.Id, teamMember.TeamId);
            Assert.AreEqual("uid", teamMember.UserId);
            Assert.AreEqual(result.CreatedAt, teamMember.CreatedAt);
        }
        #endregion

        #region UpdateTeamAsync
        [Test]
        public async Task UpdateTeamAsync_Null()
        {
            var cancellationToken = CancellationToken.None;
            var logger = new Mock<ILogger<TeamManagement>>();
            var storageContext = new Mock<IStorageContext>();

            TeamManagement teamManagement = new TeamManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
            };
            Assert.IsNull(await teamManagement.UpdateTeamAsync(null, null, cancellationToken));
            Assert.IsNull(await teamManagement.UpdateTeamAsync(new Team(), null, cancellationToken));

            TeamEntity entity = new TeamEntity();
            Assert.AreEqual(entity, await teamManagement.UpdateTeamAsync(null, entity, cancellationToken));
            Mock.VerifyAll(logger, storageContext);
            logger.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
        }

        [Test]
        public async Task UpdateTeamAsync_Updated()
        {
            var request = new Team { description = "newdesc", autoApprove = true };
            var entity = new TeamEntity
            {
                RowKey = "tid",
                Description = "desc",
                DisplayName = "dp",
                AutoApprove = false
            };

            var logger = new Mock<ILogger<TeamManagement>>();
            var teamTable = new Mock<ITeamTable>();
            teamTable.Setup(t => t.MergeAsync(entity, default));
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.TeamTable).Returns(teamTable.Object);
            var cache = new Mock<ICacheProvider>();
            cache.Setup(c => c.Remove("Team-tid"));

            TeamManagement teamManagement = new TeamManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
                Cache = cache.Object,
            };
            var result = await teamManagement.UpdateTeamAsync(request, entity, default);

            Mock.VerifyAll(logger, storageContext, teamTable, cache);
            logger.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            teamTable.VerifyNoOtherCalls();
            cache.VerifyNoOtherCalls();

            Assert.AreEqual("newdesc", result.Description);
            Assert.AreEqual("dp", result.DisplayName);
            Assert.AreEqual(true, result.AutoApprove);
        }
        #endregion

        #region UpdateTeamMembersCountAsync
        [Test]
        public async Task UpdateTeamMembersCountAsync()
        {
            string hackathonName = "hack";
            string teamId = "tid";
            var team = new TeamEntity { MembersCount = 5 };
            int count = 10;

            var teamTable = new Mock<ITeamTable>();
            teamTable.Setup(p => p.RetrieveAsync(hackathonName, teamId, default)).ReturnsAsync(team);
            var teamMemberTable = new Mock<ITeamMemberTable>();
            teamMemberTable.Setup(m => m.GetMemberCountAsync(hackathonName, teamId, default)).ReturnsAsync(count);
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.TeamTable).Returns(teamTable.Object);
            storageContext.SetupGet(p => p.TeamMemberTable).Returns(teamMemberTable.Object);
            var cache = new Mock<ICacheProvider>();
            cache.Setup(c => c.Remove("Team-tid"));

            var teamManagement = new TeamManagement(null)
            {
                StorageContext = storageContext.Object,
                Cache = cache.Object,
            };
            await teamManagement.UpdateTeamMembersCountAsync(hackathonName, teamId, default);

            Mock.VerifyAll(storageContext, teamTable, teamMemberTable);
            teamTable.Verify(t => t.MergeAsync(It.Is<TeamEntity>(t => t.MembersCount == 10), default), Times.Once);
            teamTable.VerifyNoOtherCalls();
            teamMemberTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
        }
        #endregion

        #region GetTeamByIdAsync
        [TestCase(null, null)]
        [TestCase(null, "")]
        [TestCase(null, " ")]
        [TestCase("", null)]
        [TestCase(" ", null)]
        public async Task GetTeamByIdAsync_Null(string hackName, string teamId)
        {
            var cancellationToken = CancellationToken.None;
            var logger = new Mock<ILogger<TeamManagement>>();
            TeamManagement teamManagement = new TeamManagement(logger.Object);
            var result = await teamManagement.GetTeamByIdAsync(hackName, teamId, cancellationToken);

            Mock.VerifyAll(logger);
            logger.VerifyNoOtherCalls();
            Assert.IsNull(result);
        }

        [Test]
        public async Task GetTeamByIdAsync_Succeeded()
        {
            string hackName = "Hack";
            string teamId = "tid";
            var cancellationToken = CancellationToken.None;
            TeamEntity teamEntity = new TeamEntity { Description = "desc" };

            var logger = new Mock<ILogger<TeamManagement>>();
            var teamTable = new Mock<ITeamTable>();
            teamTable.Setup(t => t.RetrieveAsync("hack", "tid", cancellationToken))
                .ReturnsAsync(teamEntity);
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.TeamTable).Returns(teamTable.Object);

            TeamManagement teamManagement = new TeamManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
                Cache = new DefaultCacheProvider(null),
            };
            var result = await teamManagement.GetTeamByIdAsync(hackName, teamId, cancellationToken);

            Mock.VerifyAll(logger, storageContext, teamTable);
            logger.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            teamTable.VerifyNoOtherCalls();
            Assert.AreEqual("desc", result.Description);
        }
        #endregion

        #region GetTeamByNameAsync
        [Test]
        public async Task GetTeamByNameAsync()
        {
            var entities = MockHelper.CreateTableQuerySegment<TeamEntity>(
                 new List<TeamEntity>
                 {
                     new TeamEntity{  PartitionKey="pk" }
                 }, null);

            var logger = new Mock<ILogger<TeamManagement>>();
            var teamTable = new Mock<ITeamTable>();
            teamTable.Setup(p => p.ExecuteQuerySegmentedAsync(
                It.Is<TableQuery<TeamEntity>>(q => q.FilterString == "(PartitionKey eq 'hack') and (DisplayName eq 'tn')"),
                It.IsAny<Action<TableQuerySegment<TeamEntity>>>(), default))
                .Callback<TableQuery<TeamEntity>, Action<TableQuerySegment<TeamEntity>>, CancellationToken>((query, c, _) =>
                {
                    c(entities);
                });
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.TeamTable).Returns(teamTable.Object);

            var teamManagement = new TeamManagement(logger.Object)
            {
                StorageContext = storageContext.Object
            };
            var result = await teamManagement.GetTeamByNameAsync("hack", "tn", default);

            Mock.VerifyAll(teamTable, storageContext);
            teamTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();

            Assert.AreEqual(1, result.Count());
            Assert.AreEqual("pk", result.First().HackathonName);
        }
        #endregion

        #region ListPaginatedTeamsAsync
        [Test]
        public async Task ListPaginatedTeamsAsync_NoOptions()
        {
            string hackName = "foo";
            TeamQueryOptions options = null;
            CancellationToken cancellationToken = CancellationToken.None;
            var entities = MockHelper.CreateTableQuerySegment<TeamEntity>(
                 new List<TeamEntity>
                 {
                     new TeamEntity{  PartitionKey="pk" }
                 },
                 new TableContinuationToken { NextPartitionKey = "np", NextRowKey = "nr" }
                );

            TableQuery<TeamEntity> tableQueryCaptured = null;
            TableContinuationToken tableContinuationTokenCapatured = null;

            var logger = new Mock<ILogger<TeamManagement>>();
            var teamTable = new Mock<ITeamTable>();
            teamTable.Setup(p => p.ExecuteQuerySegmentedAsync(It.IsAny<TableQuery<TeamEntity>>(), It.IsAny<TableContinuationToken>(), cancellationToken))
                .Callback<TableQuery<TeamEntity>, TableContinuationToken, CancellationToken>((query, c, _) =>
                {
                    tableQueryCaptured = query;
                    tableContinuationTokenCapatured = c;
                })
                .ReturnsAsync(entities);
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.TeamTable).Returns(teamTable.Object);

            var teamManagement = new TeamManagement(logger.Object)
            {
                StorageContext = storageContext.Object
            };
            var segment = await teamManagement.ListPaginatedTeamsAsync(hackName, options, cancellationToken);

            Mock.VerifyAll(teamTable, storageContext);
            teamTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();

            Assert.AreEqual(1, segment.Count());
            Assert.AreEqual("pk", segment.First().HackathonName);
            Assert.AreEqual("np", segment.ContinuationToken.NextPartitionKey);
            Assert.AreEqual("nr", segment.ContinuationToken.NextRowKey);
            Assert.IsNull(tableContinuationTokenCapatured);
            Assert.AreEqual("PartitionKey eq 'foo'", tableQueryCaptured.FilterString);
            Assert.AreEqual(100, tableQueryCaptured.TakeCount.Value);
        }

        [TestCase(5, 5)]
        [TestCase(-1, 100)]
        public async Task ListPaginatedTeamsAsync_Options(int topInPara, int expectedTop)
        {
            string hackName = "foo";
            TeamQueryOptions options = new TeamQueryOptions
            {
                TableContinuationToken = new TableContinuationToken { NextPartitionKey = "np", NextRowKey = "nr" },
                Top = topInPara,
            };
            CancellationToken cancellationToken = CancellationToken.None;
            var entities = MockHelper.CreateTableQuerySegment<TeamEntity>(
                 new List<TeamEntity>
                 {
                     new TeamEntity{  PartitionKey="pk" }
                 },
                 new TableContinuationToken { NextPartitionKey = "np2", NextRowKey = "nr2" }
                );

            TableQuery<TeamEntity> tableQueryCaptured = null;
            TableContinuationToken tableContinuationTokenCapatured = null;

            var logger = new Mock<ILogger<TeamManagement>>();
            var teamTable = new Mock<ITeamTable>();
            teamTable.Setup(p => p.ExecuteQuerySegmentedAsync(It.IsAny<TableQuery<TeamEntity>>(), It.IsAny<TableContinuationToken>(), cancellationToken))
                .Callback<TableQuery<TeamEntity>, TableContinuationToken, CancellationToken>((query, c, _) =>
                {
                    tableQueryCaptured = query;
                    tableContinuationTokenCapatured = c;
                })
                .ReturnsAsync(entities);
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.TeamTable).Returns(teamTable.Object);

            var teamManagement = new TeamManagement(logger.Object)
            {
                StorageContext = storageContext.Object
            };
            var segment = await teamManagement.ListPaginatedTeamsAsync(hackName, options, cancellationToken);

            Mock.VerifyAll(teamTable, storageContext);
            teamTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();

            Assert.AreEqual(1, segment.Count());
            Assert.AreEqual("pk", segment.First().HackathonName);
            Assert.AreEqual("np2", segment.ContinuationToken.NextPartitionKey);
            Assert.AreEqual("nr2", segment.ContinuationToken.NextRowKey);
            Assert.AreEqual("np", tableContinuationTokenCapatured.NextPartitionKey);
            Assert.AreEqual("nr", tableContinuationTokenCapatured.NextRowKey);
            Assert.AreEqual("PartitionKey eq 'foo'", tableQueryCaptured.FilterString);
            Assert.AreEqual(expectedTop, tableQueryCaptured.TakeCount.Value);
        }
        #endregion

        #region DeleteTeamAsync
        [Test]
        public async Task DeleteTeamAsync()
        {
            TeamEntity team = new TeamEntity { PartitionKey = "pk", RowKey = "rk" };
            CancellationToken cancellationToken = CancellationToken.None;

            var logger = new Mock<ILogger<TeamManagement>>();
            var teamTable = new Mock<ITeamTable>();
            teamTable.Setup(t => t.DeleteAsync("pk", "rk", cancellationToken));
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.TeamTable).Returns(teamTable.Object);
            var cache = new Mock<ICacheProvider>();
            cache.Setup(c => c.Remove("Team-rk"));

            TeamManagement teamManagement = new TeamManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
                Cache = cache.Object,
            };
            await teamManagement.DeleteTeamAsync(team, cancellationToken);

            Mock.VerifyAll(logger, teamTable, storageContext, cache);
            teamTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            cache.VerifyNoOtherCalls();
        }
        #endregion

        #region CreateTeamMemberAsync
        [Test]
        public async Task CreateTeamMemberAsync()
        {
            TeamMember request = new TeamMember { hackathonName = "hack", teamId = "tid" };
            TeamEntity team = new TeamEntity { };
            int count = 5;

            var logger = new Mock<ILogger<TeamManagement>>();
            var teamTable = new Mock<ITeamTable>();
            teamTable.Setup(p => p.RetrieveAsync("hack", "tid", default)).ReturnsAsync(team);
            var teamMemberTable = new Mock<ITeamMemberTable>();
            teamMemberTable.Setup(t => t.InsertOrMergeAsync(It.IsAny<TeamMemberEntity>(), default));
            teamMemberTable.Setup(m => m.GetMemberCountAsync("hack", "tid", default)).ReturnsAsync(count);
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.TeamTable).Returns(teamTable.Object);
            storageContext.SetupGet(p => p.TeamMemberTable).Returns(teamMemberTable.Object);
            var cache = new Mock<ICacheProvider>();
            cache.Setup(c => c.Remove("Team-tid"));

            TeamManagement teamManagement = new TeamManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
                Cache = cache.Object,
            };
            var result = await teamManagement.CreateTeamMemberAsync(request, default);

            Mock.VerifyAll(logger, teamMemberTable, storageContext);
            teamTable.Verify(t => t.MergeAsync(It.Is<TeamEntity>(t => t.MembersCount == 5), default), Times.Once);
            teamTable.VerifyNoOtherCalls();
            teamMemberTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            Assert.AreEqual("hack", result.HackathonName);
            Assert.AreEqual(TeamMemberRole.Member, result.Role);
        }
        #endregion

        #region UpdateTeamMemberAsync
        [Test]
        public async Task UpdateTeamMemberAsync()
        {
            TeamMember request = new TeamMember { description = "b" };
            CancellationToken cancellationToken = CancellationToken.None;
            TeamMemberEntity member = new TeamMemberEntity { Description = "a", Role = TeamMemberRole.Member, Status = TeamMemberStatus.pendingApproval };
            TeamMemberEntity captured = null;

            var logger = new Mock<ILogger<TeamManagement>>();
            var teamMemberTable = new Mock<ITeamMemberTable>();
            teamMemberTable.Setup(t => t.MergeAsync(It.IsAny<TeamMemberEntity>(), cancellationToken))
                .Callback<TeamMemberEntity, CancellationToken>((tm, c) => { captured = tm; });
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.TeamMemberTable).Returns(teamMemberTable.Object);

            TeamManagement teamManagement = new TeamManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
            };
            var result = await teamManagement.UpdateTeamMemberAsync(member, request, cancellationToken);

            Mock.VerifyAll(logger, teamMemberTable, storageContext);
            teamMemberTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            Assert.AreEqual("b", result.Description);
            Assert.AreEqual("b", captured.Description);
            Assert.AreEqual(TeamMemberRole.Member, result.Role);
            Assert.AreEqual(TeamMemberStatus.pendingApproval, result.Status);
        }
        #endregion

        #region GetTeamMemberAsync
        [TestCase(null, null)]
        [TestCase("", null)]
        [TestCase("", " ")]
        [TestCase(null, "")]
        [TestCase(null, " ")]
        public async Task GetTeamMember_Null(string hackName, string userId)
        {
            var logger = new Mock<ILogger<TeamManagement>>();
            TeamManagement teamManagement = new TeamManagement(logger.Object)
            {
            };
            var result = await teamManagement.GetTeamMemberAsync(hackName, userId, default);
            Assert.IsNull(result);
        }

        [Test]
        public async Task GetTeamMember_Suecceded()
        {
            string userId = "uid";
            var cancellationToken = CancellationToken.None;
            TeamMemberEntity teamMember = new TeamMemberEntity { Description = "desc" };

            var logger = new Mock<ILogger<TeamManagement>>();
            var teamMemberTable = new Mock<ITeamMemberTable>();
            teamMemberTable.Setup(t => t.RetrieveAsync("hack", "uid", cancellationToken))
                .ReturnsAsync(teamMember);
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.TeamMemberTable).Returns(teamMemberTable.Object);

            TeamManagement teamManagement = new TeamManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
            };
            var result = await teamManagement.GetTeamMemberAsync("hack", userId, cancellationToken);

            Mock.VerifyAll(logger, teamMemberTable, storageContext);
            teamMemberTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            Assert.IsNotNull(result);
            Assert.AreEqual("desc", result.Description);
        }
        #endregion

        #region UpdateTeamMemberStatusAsync
        [TestCase(TeamMemberStatus.approved)]
        [TestCase(TeamMemberStatus.pendingApproval)]
        public async Task UpdateTeamMemberStatusAsync_Skip(TeamMemberStatus status)
        {
            TeamMemberEntity teamMember = new TeamMemberEntity { Status = status };
            CancellationToken cancellationToken = CancellationToken.None;

            var logger = new Mock<ILogger<TeamManagement>>();
            var teamMemberTable = new Mock<ITeamMemberTable>();
            var storageContext = new Mock<IStorageContext>();

            TeamManagement teamManagement = new TeamManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
            };
            var result = await teamManagement.UpdateTeamMemberStatusAsync(teamMember, status, cancellationToken);

            Mock.VerifyAll(logger, teamMemberTable, storageContext);
            teamMemberTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
        }

        [TestCase(TeamMemberStatus.pendingApproval, TeamMemberStatus.approved)]
        [TestCase(TeamMemberStatus.approved, TeamMemberStatus.pendingApproval)]
        public async Task UpdateTeamMemberStatusAsync_Succeeded(TeamMemberStatus oldStatus, TeamMemberStatus newStatus)
        {
            TeamMemberEntity teamMember = new TeamMemberEntity { Status = oldStatus };
            CancellationToken cancellationToken = CancellationToken.None;
            TeamMemberEntity captured = null;

            var logger = new Mock<ILogger<TeamManagement>>();
            var teamMemberTable = new Mock<ITeamMemberTable>();
            teamMemberTable.Setup(t => t.MergeAsync(It.IsAny<TeamMemberEntity>(), cancellationToken))
                .Callback<TeamMemberEntity, CancellationToken>((tm, c) => { captured = tm; });
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.TeamMemberTable).Returns(teamMemberTable.Object);


            TeamManagement teamManagement = new TeamManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
            };
            var result = await teamManagement.UpdateTeamMemberStatusAsync(teamMember, newStatus, cancellationToken);

            Mock.VerifyAll(logger, teamMemberTable, storageContext);
            teamMemberTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            Assert.IsNull(result.Description);
            Assert.IsNull(captured.Description);
            Assert.AreEqual(newStatus, result.Status);
            Assert.AreEqual(newStatus, captured.Status);
        }
        #endregion

        #region UpdateTeamMemberRoleAsync
        [TestCase(TeamMemberRole.Member)]
        [TestCase(TeamMemberRole.Admin)]
        public async Task UpdateTeamMemberRoleAsync_Skip(TeamMemberRole role)
        {
            TeamMemberEntity teamMember = new TeamMemberEntity { Role = role };
            CancellationToken cancellationToken = CancellationToken.None;

            var logger = new Mock<ILogger<TeamManagement>>();
            var teamMemberTable = new Mock<ITeamMemberTable>();
            var storageContext = new Mock<IStorageContext>();

            TeamManagement teamManagement = new TeamManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
            };
            var result = await teamManagement.UpdateTeamMemberRoleAsync(teamMember, role, cancellationToken);

            Mock.VerifyAll(logger, teamMemberTable, storageContext);
            teamMemberTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
        }

        [TestCase(TeamMemberRole.Member, TeamMemberRole.Admin)]
        [TestCase(TeamMemberRole.Admin, TeamMemberRole.Member)]
        public async Task UpdateTeamMemberRoleAsync_Succeeded(TeamMemberRole oldRole, TeamMemberRole newRole)
        {
            TeamMemberEntity teamMember = new TeamMemberEntity { Role = oldRole };
            CancellationToken cancellationToken = CancellationToken.None;
            TeamMemberEntity captured = null;

            var logger = new Mock<ILogger<TeamManagement>>();
            var teamMemberTable = new Mock<ITeamMemberTable>();
            teamMemberTable.Setup(t => t.MergeAsync(It.IsAny<TeamMemberEntity>(), cancellationToken))
                .Callback<TeamMemberEntity, CancellationToken>((tm, c) => { captured = tm; });
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.TeamMemberTable).Returns(teamMemberTable.Object);


            TeamManagement teamManagement = new TeamManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
            };
            var result = await teamManagement.UpdateTeamMemberRoleAsync(teamMember, newRole, cancellationToken);

            Mock.VerifyAll(logger, teamMemberTable, storageContext);
            teamMemberTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            Assert.IsNull(result.Description);
            Assert.IsNull(captured.Description);
            Assert.AreEqual(newRole, result.Role);
            Assert.AreEqual(newRole, captured.Role);
        }
        #endregion

        #region DeleteTeamMemberAsync
        [Test]
        public async Task DeleteTeamMemberAsync()
        {
            TeamMemberEntity teamMember = new TeamMemberEntity { PartitionKey = "hack", RowKey = "uid", TeamId = "tid" };
            TeamEntity team = new TeamEntity { };
            int count = 5;

            var logger = new Mock<ILogger<TeamManagement>>();
            var teamTable = new Mock<ITeamTable>();
            teamTable.Setup(p => p.RetrieveAsync("hack", "tid", default)).ReturnsAsync(team);
            var teamMemberTable = new Mock<ITeamMemberTable>();
            teamMemberTable.Setup(t => t.DeleteAsync("hack", "uid", default));
            teamMemberTable.Setup(m => m.GetMemberCountAsync("hack", "tid", default)).ReturnsAsync(count);
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.TeamMemberTable).Returns(teamMemberTable.Object);
            storageContext.SetupGet(p => p.TeamTable).Returns(teamTable.Object);
            var cache = new Mock<ICacheProvider>();
            cache.Setup(c => c.Remove("Team-tid"));

            TeamManagement teamManagement = new TeamManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
                Cache = cache.Object,
            };
            await teamManagement.DeleteTeamMemberAsync(teamMember, default);

            Mock.VerifyAll(storageContext, teamTable, teamMemberTable, cache);
            teamTable.Verify(t => t.MergeAsync(It.Is<TeamEntity>(t => t.MembersCount == 5), default), Times.Once);
            teamTable.VerifyNoOtherCalls();
            teamMemberTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            cache.VerifyNoOtherCalls();
        }
        #endregion

        #region ListTeamMembersAsync
        [Test]
        public async Task ListTeamMembersAsync()
        {
            var cancellationToken = CancellationToken.None;
            List<TeamMemberEntity> teamMembers = new List<TeamMemberEntity>
            {
                new TeamMemberEntity
                {
                    RowKey = "rk1",
                    Role = TeamMemberRole.Admin,
                    Status = TeamMemberStatus.approved
                },
                new TeamMemberEntity
                {
                    RowKey = "rk2",
                    Role = TeamMemberRole.Member,
                    Status = TeamMemberStatus.pendingApproval
                },
            };

            string query = null;
            TableContinuationToken continuationToken = null;
            var logger = new Mock<ILogger<TeamManagement>>();
            var teamMemberTable = new Mock<ITeamMemberTable>();
            teamMemberTable.Setup(p => p.ExecuteQuerySegmentedAsync(It.IsAny<TableQuery<TeamMemberEntity>>(), It.IsAny<TableContinuationToken>(), cancellationToken))
                .Callback<TableQuery<TeamMemberEntity>, TableContinuationToken, CancellationToken>((q, t, c) =>
                {
                    query = q.FilterString;
                    continuationToken = t;
                })
                .ReturnsAsync(MockHelper.CreateTableQuerySegment(teamMembers, null));
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.TeamMemberTable).Returns(teamMemberTable.Object);
            var cache = new DefaultCacheProvider(null);

            var teamManagement = new TeamManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
                Cache = cache,
            };
            var results = await teamManagement.ListTeamMembersAsync("hack", "tid", cancellationToken);

            Mock.VerifyAll(logger, teamMemberTable, storageContext);
            Assert.AreEqual("(PartitionKey eq 'hack') and (TeamId eq 'tid')", query);
            Assert.IsNull(continuationToken);
            Assert.AreEqual(2, results.Count());
            Assert.AreEqual("rk1", results.First().UserId);
            Assert.AreEqual(TeamMemberRole.Admin, results.First().Role);
            Assert.AreEqual(TeamMemberStatus.approved, results.First().Status);
            Assert.AreEqual("rk2", results.Last().UserId);
            Assert.AreEqual(TeamMemberRole.Member, results.Last().Role);
            Assert.AreEqual(TeamMemberStatus.pendingApproval, results.Last().Status);
        }
        #endregion

        #region ListPaginatedTeamMembersAsync

        private static IEnumerable ListPaginatedTeamMembersAsyncTestData()
        {
            // arg0: options
            // arg1: expected top
            // arg2: expected query

            // no options
            yield return new TestCaseData(
                null,
                100,
                "(PartitionKey eq 'hack') and (TeamId eq 'tid')"
                );

            // top
            yield return new TestCaseData(
                new TeamMemberQueryOptions { Top = 5 },
                5,
                "(PartitionKey eq 'hack') and (TeamId eq 'tid')"
                );
            yield return new TestCaseData(
               new TeamMemberQueryOptions { Top = -1 },
               100,
               "(PartitionKey eq 'hack') and (TeamId eq 'tid')"
               );

            // status
            yield return new TestCaseData(
               new TeamMemberQueryOptions { Status = TeamMemberStatus.approved },
               100,
               "((PartitionKey eq 'hack') and (TeamId eq 'tid')) and (Status eq 1)"
               );
            yield return new TestCaseData(
               new TeamMemberQueryOptions { Status = TeamMemberStatus.pendingApproval },
               100,
               "((PartitionKey eq 'hack') and (TeamId eq 'tid')) and (Status eq 0)"
               );

            // Role
            yield return new TestCaseData(
               new TeamMemberQueryOptions { Role = TeamMemberRole.Admin },
               100,
               "((PartitionKey eq 'hack') and (TeamId eq 'tid')) and (Role eq 0)"
               );
            yield return new TestCaseData(
               new TeamMemberQueryOptions { Role = TeamMemberRole.Member },
               100,
               "((PartitionKey eq 'hack') and (TeamId eq 'tid')) and (Role eq 1)"
               );

            // all options
            yield return new TestCaseData(
               new TeamMemberQueryOptions
               {
                   Top = 20,
                   Role = TeamMemberRole.Member,
                   Status = TeamMemberStatus.approved,
               },
               20,
               "(((PartitionKey eq 'hack') and (TeamId eq 'tid')) and (Status eq 1)) and (Role eq 1)"
               );
        }

        [Test, TestCaseSource(nameof(ListPaginatedTeamMembersAsyncTestData))]
        public async Task ListPaginatedTeamMembersAsync_Options(TeamMemberQueryOptions options, int expectedTop, string expectedFilter)
        {
            string hackName = "hack";
            CancellationToken cancellationToken = CancellationToken.None;
            var entities = MockHelper.CreateTableQuerySegment<TeamMemberEntity>(
                 new List<TeamMemberEntity>
                 {
                     new TeamMemberEntity{  TeamId="tid" }
                 },
                 new TableContinuationToken { NextPartitionKey = "np", NextRowKey = "nr" }
                );

            TableQuery<TeamMemberEntity> tableQueryCaptured = null;
            TableContinuationToken tableContinuationTokenCapatured = null;

            var logger = new Mock<ILogger<TeamManagement>>();
            var teamMemberTable = new Mock<ITeamMemberTable>();
            teamMemberTable.Setup(p => p.ExecuteQuerySegmentedAsync(It.IsAny<TableQuery<TeamMemberEntity>>(), It.IsAny<TableContinuationToken>(), cancellationToken))
                .Callback<TableQuery<TeamMemberEntity>, TableContinuationToken, CancellationToken>((query, c, _) =>
                {
                    tableQueryCaptured = query;
                    tableContinuationTokenCapatured = c;
                })
                .ReturnsAsync(entities);
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.TeamMemberTable).Returns(teamMemberTable.Object);

            var teamManagement = new TeamManagement(logger.Object)
            {
                StorageContext = storageContext.Object
            };
            var segment = await teamManagement.ListPaginatedTeamMembersAsync(hackName, "tid", options, cancellationToken);

            Mock.VerifyAll(teamMemberTable, storageContext);
            teamMemberTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();

            Assert.AreEqual(1, segment.Count());
            Assert.AreEqual("tid", segment.First().TeamId);
            Assert.AreEqual("np", segment.ContinuationToken.NextPartitionKey);
            Assert.AreEqual("nr", segment.ContinuationToken.NextRowKey);
            Assert.IsNull(tableContinuationTokenCapatured);
            Assert.AreEqual(expectedFilter, tableQueryCaptured.FilterString);
            Assert.AreEqual(expectedTop, tableQueryCaptured.TakeCount.Value);
        }

        #endregion
    }
}
