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
    public class JudgeManagementTests
    {
        #region CanCreateJudgeAsync
        private static IEnumerable CanCreateJudgeAsyncTestData()
        {
            // arg0: judges
            // arg1: expectedResult

            List<JudgeEntity> notexceed = new List<JudgeEntity>();
            for (int i = 0; i < 99; i++)
            {
                notexceed.Add(new JudgeEntity());
            }

            // not exceed
            yield return new TestCaseData(notexceed, true);

            // exceed
            List<JudgeEntity> exceed = new List<JudgeEntity>();
            for (int i = 0; i < 100; i++)
            {
                exceed.Add(new JudgeEntity());
            }
            yield return new TestCaseData(exceed, false);
        }

        [Test, TestCaseSource(nameof(CanCreateJudgeAsyncTestData))]
        public async Task CanCreateJudgeAsync(List<JudgeEntity> judges, bool expectedResult)
        {
            var logger = new Mock<ILogger<JudgeManagement>>();
            var cache = new Mock<ICacheProvider>();
            cache.Setup(c => c.GetOrAddAsync(It.Is<CacheEntry<IEnumerable<JudgeEntity>>>(c => c.CacheKey == "Judge-hack"), default))
                .ReturnsAsync(judges);

            var judgeManagement = new JudgeManagement(logger.Object)
            {
                Cache = cache.Object,
            };
            var result = await judgeManagement.CanCreateJudgeAsync("hack", default);

            Mock.VerifyAll(cache);
            cache.VerifyNoOtherCalls();

            Assert.AreEqual(expectedResult, result);
        }
        #endregion

        #region CreateJudgeAsync
        [Test]
        public async Task CreateJudgeAsync()
        {
            Judge parameter = new Judge
            {
                hackathonName = "hack",
                description = "desc",
                userId = "uid"
            };

            var logger = new Mock<ILogger<JudgeManagement>>();
            var judgeTable = new Mock<IJudgeTable>();
            judgeTable.Setup(j => j.InsertOrReplaceAsync(It.Is<JudgeEntity>(en =>
                en.Description == "desc" &&
                en.PartitionKey == "hack" &&
                en.HackathonName == "hack" &&
                en.RowKey == "uid" &&
                en.UserId == "uid"), default));
            var storageContext = new Mock<IStorageContext>();
            storageContext.Setup(s => s.JudgeTable).Returns(judgeTable.Object);
            var cache = new Mock<ICacheProvider>();
            cache.Setup(c => c.Remove("Judge-hack"));

            var judgeManagement = new JudgeManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
                Cache = cache.Object,
            };
            var result = await judgeManagement.CreateJudgeAsync(parameter, default);

            Mock.VerifyAll(judgeTable, storageContext, cache);
            judgeTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            cache.VerifyNoOtherCalls();

            Assert.AreEqual("desc", result.Description);
            Assert.AreEqual("hack", result.HackathonName);
            Assert.AreEqual("uid", result.UserId);
        }
        #endregion

        #region UpdateJudgeAsync
        [TestCase(null, "desc")]
        [TestCase("desc2", "desc2")]
        public async Task UpdateJudgeAsync(string requestedDesc, string expectedDesc)
        {
            JudgeEntity existing = new JudgeEntity { Description = "desc" };
            Judge parameter = new Judge { hackathonName = "hack", description = requestedDesc };

            var logger = new Mock<ILogger<JudgeManagement>>();
            var judgeTable = new Mock<IJudgeTable>();
            judgeTable.Setup(j => j.MergeAsync(It.Is<JudgeEntity>(en => en.Description == expectedDesc), default));
            var storageContext = new Mock<IStorageContext>();
            storageContext.Setup(s => s.JudgeTable).Returns(judgeTable.Object);
            var cache = new Mock<ICacheProvider>();
            cache.Setup(c => c.Remove("Judge-hack"));

            var judgeManagement = new JudgeManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
                Cache = cache.Object,
            };
            var result = await judgeManagement.UpdateJudgeAsync(existing, parameter, default);

            Mock.VerifyAll(judgeTable, storageContext, cache);
            judgeTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            cache.VerifyNoOtherCalls();

            Assert.AreEqual(expectedDesc, result.Description);
        }
        #endregion

        #region GetJudgeAsync
        [Test]
        public async Task GetJudgeAsync()
        {
            var judge = new JudgeEntity { PartitionKey = "pk" };

            var logger = new Mock<ILogger<JudgeManagement>>();
            var judgeTable = new Mock<IJudgeTable>();
            judgeTable.Setup(j => j.RetrieveAsync("hack", "uid", default)).ReturnsAsync(judge);
            var storageContext = new Mock<IStorageContext>();
            storageContext.Setup(s => s.JudgeTable).Returns(judgeTable.Object);

            var judgeManagement = new JudgeManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
            };
            var result = await judgeManagement.GetJudgeAsync("hack", "uid", default);

            Mock.VerifyAll(judgeTable, storageContext);
            judgeTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();

            Assert.AreEqual("pk", result.HackathonName);
        }
        #endregion

        #region IsJudgeAsync
        private static IEnumerable IsJudgeAsyncTestData()
        {
            var a1 = new JudgeEntity { RowKey = "user1", };
            var a2 = new JudgeEntity { RowKey = "user2", };
            var a3 = new JudgeEntity { RowKey = "user3", };
            // arg0: judges
            // arg1: userId
            // arg2: expected result
            yield return new TestCaseData(
                new List<JudgeEntity> { a1, a2, a3 },
                "user1",
                true
                );

            yield return new TestCaseData(
                new List<JudgeEntity> { a1, a2, a3 },
                "user4",
                false
                );
        }

        [Test, TestCaseSource(nameof(IsJudgeAsyncTestData))]
        public async Task IsJudgeAsync(List<JudgeEntity> judges, string userId, bool expectedResult)
        {
            var logger = new Mock<ILogger<JudgeManagement>>();
            var cache = new Mock<ICacheProvider>();
            cache.Setup(c => c.GetOrAddAsync(It.Is<CacheEntry<IEnumerable<JudgeEntity>>>(c => c.CacheKey == "Judge-hack"), default)).ReturnsAsync(judges);

            var judgeManagement = new JudgeManagement(logger.Object)
            {
                Cache = cache.Object,
            };
            var result = await judgeManagement.IsJudgeAsync("hack", userId, default);

            Mock.VerifyAll(cache);
            cache.VerifyNoOtherCalls();
            Assert.AreEqual(expectedResult, result);
        }
        #endregion

        #region ListPaginatedJudgesAsync

        private static IEnumerable ListPaginatedJudgesAsyncTestData()
        {
            var a1 = new JudgeEntity
            {
                RowKey = "a1",
                CreatedAt = DateTime.UtcNow.AddDays(1),
            };
            var a2 = new JudgeEntity
            {
                RowKey = "a1",
                CreatedAt = DateTime.UtcNow.AddDays(3),
            };
            var a3 = new JudgeEntity
            {
                RowKey = "a1",
                CreatedAt = DateTime.UtcNow.AddDays(2),
            };
            var a4 = new JudgeEntity
            {
                RowKey = "a1",
                CreatedAt = DateTime.UtcNow.AddDays(4),
            };

            // arg0: options
            // arg1: awards
            // arg2: expected result
            // arg3: expected Next

            // by Award
            yield return new TestCaseData(
                new JudgeQueryOptions { },
                new List<JudgeEntity> { a1, a2, a3, a4 },
                new List<JudgeEntity> { a4, a2, a3, a1 },
                null
                );

            // by Team
            yield return new TestCaseData(
                new JudgeQueryOptions { },
                new List<JudgeEntity> { a1, a2, a3, a4 },
                new List<JudgeEntity> { a4, a2, a3, a1 },
                null
                );

            // by Hackathon
            yield return new TestCaseData(
                new JudgeQueryOptions { },
                new List<JudgeEntity> { a1, a2, a3, a4 },
                new List<JudgeEntity> { a4, a2, a3, a1 },
                null
                );

            // top
            yield return new TestCaseData(
                new JudgeQueryOptions { Top = 2, },
                new List<JudgeEntity> { a1, a2, a3, a4 },
                new List<JudgeEntity> { a4, a2, },
                new TableContinuationToken { NextPartitionKey = "2", NextRowKey = "2" }
                );

            // paging
            yield return new TestCaseData(
                new JudgeQueryOptions
                {
                    Top = 2,
                    TableContinuationToken = new TableContinuationToken
                    {
                        NextPartitionKey = "1",
                        NextRowKey = "1"
                    },
                },
                new List<JudgeEntity> { a1, a2, a3, a4 },
                new List<JudgeEntity> { a2, a3, },
                new TableContinuationToken { NextPartitionKey = "3", NextRowKey = "3" }
                );
        }

        [Test, TestCaseSource(nameof(ListPaginatedJudgesAsyncTestData))]
        public async Task ListPaginatedAssignmentsAsync(
            JudgeQueryOptions options,
            IEnumerable<JudgeEntity> all,
            IEnumerable<JudgeEntity> expectedResult,
            TableContinuationToken expectedNext)
        {
            string hackName = "hack";

            var logger = new Mock<ILogger<JudgeManagement>>();
            var cache = new Mock<ICacheProvider>();
            cache.Setup(c => c.GetOrAddAsync(It.Is<CacheEntry<IEnumerable<JudgeEntity>>>(c => c.CacheKey == "Judge-hack"), default)).ReturnsAsync(all);

            var judgeManagement = new JudgeManagement(logger.Object)
            {
                Cache = cache.Object,
            };
            var result = await judgeManagement.ListPaginatedJudgesAsync(hackName, options, default);

            Mock.VerifyAll(cache);
            cache.VerifyNoOtherCalls();

            Assert.AreEqual(expectedResult.Count(), result.Count());
            for (int i = 0; i < expectedResult.Count(); i++)
            {
                Assert.AreEqual(expectedResult.ElementAt(i).UserId, result.ElementAt(i).UserId);
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

        #region DeleteJudgeAsync
        [Test]
        public async Task DeleteJudgeAsync()
        {
            var logger = new Mock<ILogger<JudgeManagement>>();
            var judgeTable = new Mock<IJudgeTable>();
            judgeTable.Setup(j => j.DeleteAsync("hack", "uid", default));
            var storageContext = new Mock<IStorageContext>();
            storageContext.Setup(s => s.JudgeTable).Returns(judgeTable.Object);

            var judgeManagement = new JudgeManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
            };
            await judgeManagement.DeleteJudgeAsync("hack", "uid", default);

            Mock.VerifyAll(judgeTable, storageContext);
            judgeTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
        }
        #endregion
    }
}
