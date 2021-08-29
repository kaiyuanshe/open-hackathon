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
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Biz
{
    public class WorkManagementTests
    {
        #region CanCreateTeamWorkAsync
        private static IEnumerable CanCreateTeamWorkAsyncTestData()
        {
            // arg0: judges
            // arg1: expectedResult

            List<TeamWorkEntity> notexceed = new List<TeamWorkEntity>();
            for (int i = 0; i < 99; i++)
            {
                notexceed.Add(new TeamWorkEntity());
            }

            // not exceed
            yield return new TestCaseData(notexceed, true);

            // exceed
            List<TeamWorkEntity> exceed = new List<TeamWorkEntity>();
            for (int i = 0; i < 100; i++)
            {
                exceed.Add(new TeamWorkEntity());
            }
            yield return new TestCaseData(exceed, false);
        }

        [Test, TestCaseSource(nameof(CanCreateTeamWorkAsyncTestData))]
        public async Task CanCreateTeamWorkAsync(List<TeamWorkEntity> judges, bool expectedResult)
        {
            var logger = new Mock<ILogger<WorkManagement>>();
            var cache = new Mock<ICacheProvider>();
            cache.Setup(c => c.GetOrAddAsync(It.Is<CacheEntry<IEnumerable<TeamWorkEntity>>>(c => c.CacheKey == "TeamWork-tid"), default))
                .ReturnsAsync(judges);

            var workManagement = new WorkManagement(logger.Object)
            {
                Cache = cache.Object,
            };
            var result = await workManagement.CanCreateTeamWorkAsync("hack", "tid", default);

            Mock.VerifyAll(cache);
            cache.VerifyNoOtherCalls();

            Assert.AreEqual(expectedResult, result);
        }
        #endregion

        #region CreateTeamWorkAsync
        [TestCase(null)]
        [TestCase(TeamWorkType.video)]
        public async Task CreateTeamWorkAsync(TeamWorkType? type)
        {
            // input
            TeamWork request = new TeamWork
            {
                description = "desc",
                hackathonName = "hack",
                teamId = "teamId",
                title = "title",
                type = type,
                url = "url"
            };

            // mock
            var logger = new Mock<ILogger<WorkManagement>>();
            var teamWorkTable = new Mock<ITeamWorkTable>();
            teamWorkTable.Setup(p => p.InsertAsync(It.Is<TeamWorkEntity>(e => e.Description == "desc"
                && e.HackathonName == "hack"
                && e.TeamId == "teamId"
                && e.Title == "title"
                && e.Url == "url"
                && e.Type == type.GetValueOrDefault(TeamWorkType.website)), default));
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.TeamWorkTable).Returns(teamWorkTable.Object);
            var cache = new Mock<ICacheProvider>();
            cache.Setup(c => c.Remove("TeamWork-teamId"));

            // test
            var workManagement = new WorkManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
                Cache = cache.Object,
            };
            var result = await workManagement.CreateTeamWorkAsync(request, default);


            // verify
            Mock.VerifyAll(teamWorkTable, storageContext, cache);
            teamWorkTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            cache.VerifyNoOtherCalls();
        }
        #endregion

        #region UpdateTeamWorkAsync
        [Test]
        public async Task UpdateTeamWorkAsync()
        {
            // input
            TeamWorkEntity existing = new TeamWorkEntity
            {
                PartitionKey = "hack1",
                RowKey = "rk",
                TeamId = "teamId1",
                Description = "desc1",
                Title = "title1",
                Type = TeamWorkType.image,
                Url = "url1",
            };
            TeamWork request = new TeamWork
            {
                description = "desc2",
                hackathonName = "hack2",
                teamId = "teamId2",
                title = "title2",
                type = TeamWorkType.powerpoint,
                url = "url2"
            };

            // mock
            var logger = new Mock<ILogger<WorkManagement>>();
            var teamWorkTable = new Mock<ITeamWorkTable>();
            teamWorkTable.Setup(p => p.MergeAsync(It.Is<TeamWorkEntity>(e => e.Description == "desc2"
                && e.HackathonName == "hack1"
                && e.TeamId == "teamId1"
                && e.Title == "title2"
                && e.Url == "url2"
                && e.Type == TeamWorkType.powerpoint), default));
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.TeamWorkTable).Returns(teamWorkTable.Object);
            var cache = new Mock<ICacheProvider>();
            cache.Setup(c => c.Remove("TeamWork-teamId1"));

            // test
            var workManagement = new WorkManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
                Cache = cache.Object,
            };
            var result = await workManagement.UpdateTeamWorkAsync(existing, request, default);

            // verify
            Mock.VerifyAll(teamWorkTable, storageContext, cache);
            teamWorkTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            cache.VerifyNoOtherCalls();
        }
        #endregion

        #region GetTeamWorkAsync
        [Test]
        public async Task GetTeamWorkAsync()
        {
            var teamWork = new TeamWorkEntity { PartitionKey = "hack" };

            // mock
            var logger = new Mock<ILogger<WorkManagement>>();
            var teamWorkTable = new Mock<ITeamWorkTable>();
            teamWorkTable.Setup(p => p.RetrieveAsync("hack", "wid", default)).ReturnsAsync(teamWork);
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.TeamWorkTable).Returns(teamWorkTable.Object);

            // test
            var workManagement = new WorkManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
            };
            var result = await workManagement.GetTeamWorkAsync("hack", "wid", default);

            // verify
            Mock.VerifyAll(teamWorkTable, storageContext);
            teamWorkTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            Assert.AreEqual("hack", result.HackathonName);
        }
        #endregion

        #region ListPaginatedWorksAsync

        private static IEnumerable ListPaginatedWorksAsyncTestData()
        {
            var a1 = new TeamWorkEntity
            {
                RowKey = "a1",
                CreatedAt = DateTime.UtcNow.AddDays(1),
            };
            var a2 = new TeamWorkEntity
            {
                RowKey = "a1",
                CreatedAt = DateTime.UtcNow.AddDays(3),
            };
            var a3 = new TeamWorkEntity
            {
                RowKey = "a1",
                CreatedAt = DateTime.UtcNow.AddDays(2),
            };
            var a4 = new TeamWorkEntity
            {
                RowKey = "a1",
                CreatedAt = DateTime.UtcNow.AddDays(4),
            };

            // arg0: options
            // arg1: works
            // arg2: expected result
            // arg3: expected Next

            // by team
            yield return new TestCaseData(
                new TeamWorkQueryOptions { },
                new List<TeamWorkEntity> { a1, a2, a3, a4 },
                new List<TeamWorkEntity> { a4, a2, a3, a1 },
                null
                );

            // top
            yield return new TestCaseData(
                new TeamWorkQueryOptions { Top = 2 },
                new List<TeamWorkEntity> { a1, a2, a3, a4 },
                new List<TeamWorkEntity> { a4, a2, },
                new TableContinuationToken { NextPartitionKey = "2", NextRowKey = "2" }
                );

            // paging
            yield return new TestCaseData(
                new TeamWorkQueryOptions
                {
                    Top = 2,
                    TableContinuationToken = new TableContinuationToken
                    {
                        NextPartitionKey = "1",
                        NextRowKey = "1"
                    },
                },
                new List<TeamWorkEntity> { a1, a2, a3, a4 },
                new List<TeamWorkEntity> { a2, a3, },
                new TableContinuationToken { NextPartitionKey = "3", NextRowKey = "3" }
                );
        }

        [Test, TestCaseSource(nameof(ListPaginatedWorksAsyncTestData))]
        public async Task ListPaginatedWorksAsync(
            TeamWorkQueryOptions options,
            IEnumerable<TeamWorkEntity> allWorks,
            IEnumerable<TeamWorkEntity> expectedResult,
            TableContinuationToken expectedNext)
        {
            string teamId = "teamId";

            var logger = new Mock<ILogger<WorkManagement>>();
            var cache = new Mock<ICacheProvider>();
            cache.Setup(c => c.GetOrAddAsync(It.Is<CacheEntry<IEnumerable<TeamWorkEntity>>>(c => c.CacheKey == "TeamWork-teamId"), default))
              .ReturnsAsync(allWorks);

            var awardManagement = new WorkManagement(logger.Object)
            {
                Cache = cache.Object,
            };
            var result = await awardManagement.ListPaginatedWorksAsync("hack", teamId, options, default);

            Mock.VerifyAll(cache);
            cache.VerifyNoOtherCalls();

            Assert.AreEqual(expectedResult.Count(), result.Count());
            for (int i = 0; i < expectedResult.Count(); i++)
            {
                Assert.AreEqual(expectedResult.ElementAt(i).Id, result.ElementAt(i).Id);
            }
            if (expectedNext == null)
            {
                Assert.IsNull(options.Next);
            }
            else
            {
                Assert.IsNotNull(options.Next);
                Assert.AreEqual(expectedNext.NextPartitionKey, options.Next.NextPartitionKey);
                Assert.AreEqual(expectedNext.NextRowKey, options.Next.NextRowKey);
            }
        }
        #endregion

        #region DeleteTeamWorkAsync
        [Test]
        public async Task DeleteTeamWorkAsync()
        {
            var logger = new Mock<ILogger<WorkManagement>>();
            var teamWorkTable = new Mock<ITeamWorkTable>();
            teamWorkTable.Setup(t => t.DeleteAsync("hack", "workId", default));
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.TeamWorkTable).Returns(teamWorkTable.Object);

            WorkManagement workManagement = new WorkManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
            };
            await workManagement.DeleteTeamWorkAsync("hack", "workId", default);

            Mock.VerifyAll(teamWorkTable, storageContext);
            teamWorkTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
        }
        #endregion
    }
}
