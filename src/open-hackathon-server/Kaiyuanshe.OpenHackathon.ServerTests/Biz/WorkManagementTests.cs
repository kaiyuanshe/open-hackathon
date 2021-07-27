﻿using Kaiyuanshe.OpenHackathon.Server.Biz;
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

        #region GetTeamWorkAsync
        [Test]
        public async Task GetTeamWorkAsync()
        {
            var teamWork = new TeamWorkEntity { HackathonName = "hack" };

            // mock
            var logger = new Mock<ILogger<WorkManagement>>();
            var teamWorkTable = new Mock<ITeamWorkTable>();
            teamWorkTable.Setup(p => p.RetrieveAsync("tid", "wid", default)).ReturnsAsync(teamWork);
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.TeamWorkTable).Returns(teamWorkTable.Object);

            // test
            var workManagement = new WorkManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
            };
            var result = await workManagement.GetTeamWorkAsync("tid", "wid", default);

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
            var result = await awardManagement.ListPaginatedWorksAsync(teamId, options, default);

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

    }
}