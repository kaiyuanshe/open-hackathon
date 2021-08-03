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
    }
}
