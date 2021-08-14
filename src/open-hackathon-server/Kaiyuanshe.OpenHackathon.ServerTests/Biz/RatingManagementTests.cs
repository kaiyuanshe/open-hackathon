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
    public class RatingManagementTests
    {
        #region CreateRatingKindAsync
        [TestCase(null, 10)]
        [TestCase(5, 5)]
        public async Task CreateRatingKindAsync(int? maxRating, int expectedMaxRating)
        {
            RatingKind parameter = new RatingKind
            {
                name = "name",
                description = "desc",
                hackathonName = "hack",
                maximumScore = maxRating,
            };

            var logger = new Mock<ILogger<RatingManagement>>();
            var ratingKindTable = new Mock<IRatingKindTable>();
            ratingKindTable.Setup(t => t.InsertAsync(It.Is<RatingKindEntity>(en =>
                en.Name == "name" &&
                en.Description == "desc" &&
                en.PartitionKey == "hack" &&
                en.MaximumScore == expectedMaxRating &&
                !string.IsNullOrWhiteSpace(en.Id) &&
                en.CreatedAt > DateTime.UtcNow.AddMinutes(-1)), default));
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(s => s.RatingKindTable).Returns(ratingKindTable.Object);
            var cache = new Mock<ICacheProvider>();
            cache.Setup(c => c.Remove("RatingKind-hack"));

            var ratingManagement = new RatingManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
                Cache = cache.Object,
            };
            var result = await ratingManagement.CreateRatingKindAsync(parameter, default);

            Mock.VerifyAll(storageContext, ratingKindTable, cache);
            ratingKindTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            cache.VerifyNoOtherCalls();

            Assert.AreEqual("name", result.Name);
            Assert.AreEqual("desc", result.Description);
            Assert.AreEqual("hack", result.HackathonName);
            Assert.AreEqual(expectedMaxRating, result.MaximumScore);
        }
        #endregion

        #region UpdateRatingKindAsync
        [TestCase(null, 4)]
        [TestCase(8, 8)]
        public async Task UpdateRatingKindAsync(int? newMaxRating, int expectedNewValue)
        {
            RatingKindEntity existing = new RatingKindEntity
            {
                PartitionKey = "pk",
                Name = "n1",
                Description = "d1",
                MaximumScore = 4
            };
            RatingKind parameter = new RatingKind { name = "n2", description = "d2", maximumScore = newMaxRating };

            var logger = new Mock<ILogger<RatingManagement>>();
            var ratingKindTable = new Mock<IRatingKindTable>();
            ratingKindTable.Setup(t => t.MergeAsync(It.Is<RatingKindEntity>(en =>
                en.Name == "n2" &&
                en.Description == "d2" &&
                en.MaximumScore == expectedNewValue), default));
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(s => s.RatingKindTable).Returns(ratingKindTable.Object);
            var cache = new Mock<ICacheProvider>();
            cache.Setup(c => c.Remove("RatingKind-pk"));

            var ratingManagement = new RatingManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
                Cache = cache.Object,
            };
            var result = await ratingManagement.UpdateRatingKindAsync(existing, parameter, default);

            Mock.VerifyAll(storageContext, ratingKindTable, cache);
            ratingKindTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            cache.VerifyNoOtherCalls();

            Assert.AreEqual("n2", result.Name);
            Assert.AreEqual("d2", result.Description);
            Assert.AreEqual("pk", result.HackathonName);
            Assert.AreEqual(expectedNewValue, result.MaximumScore);
        }
        #endregion

        #region GetRatingKindAsync
        [Test]
        public async Task GetRatingKindAsync()
        {
            RatingKindEntity kind = new RatingKindEntity { PartitionKey = "pk" };

            var logger = new Mock<ILogger<RatingManagement>>();
            var ratingKindTable = new Mock<IRatingKindTable>();
            ratingKindTable.Setup(t => t.RetrieveAsync("hack", "kid", default)).ReturnsAsync(kind);
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(s => s.RatingKindTable).Returns(ratingKindTable.Object);

            var ratingManagement = new RatingManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
            };
            var result = await ratingManagement.GetRatingKindAsync("hack", "kid", default);

            Mock.VerifyAll(storageContext, ratingKindTable);
            ratingKindTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();

            Assert.AreEqual("pk", result.HackathonName);
        }
        #endregion

        #region ListPaginatedRatingKindsAsync

        private static IEnumerable ListPaginatedRatingKindsAsyncTestData()
        {
            var a1 = new RatingKindEntity
            {
                RowKey = "a1",
                CreatedAt = DateTime.UtcNow.AddDays(1),
            };
            var a2 = new RatingKindEntity
            {
                RowKey = "a1",
                CreatedAt = DateTime.UtcNow.AddDays(3),
            };
            var a3 = new RatingKindEntity
            {
                RowKey = "a1",
                CreatedAt = DateTime.UtcNow.AddDays(2),
            };
            var a4 = new RatingKindEntity
            {
                RowKey = "a1",
                CreatedAt = DateTime.UtcNow.AddDays(4),
            };

            // arg0: options
            // arg1: all kinds
            // arg2: expected result
            // arg3: expected Next

            // minimal
            yield return new TestCaseData(
                new RatingKindQueryOptions { },
                new List<RatingKindEntity> { a1, a2, a3, a4 },
                new List<RatingKindEntity> { a4, a2, a3, a1 },
                null
                );

            // top
            yield return new TestCaseData(
                new RatingKindQueryOptions { Top = 2 },
                new List<RatingKindEntity> { a1, a2, a3, a4 },
                new List<RatingKindEntity> { a4, a2, },
                new TableContinuationToken { NextPartitionKey = "2", NextRowKey = "2" }
                );

            // paging
            yield return new TestCaseData(
                new RatingKindQueryOptions
                {
                    Top = 2,
                    TableContinuationToken = new TableContinuationToken
                    {
                        NextPartitionKey = "1",
                        NextRowKey = "1"
                    }
                },
                new List<RatingKindEntity> { a1, a2, a3, a4 },
                new List<RatingKindEntity> { a2, a3, },
                new TableContinuationToken { NextPartitionKey = "3", NextRowKey = "3" }
                );
        }

        [Test, TestCaseSource(nameof(ListPaginatedRatingKindsAsyncTestData))]
        public async Task ListPaginatedAwardsAsync_Options(
            RatingKindQueryOptions options,
            IEnumerable<RatingKindEntity> allAwards,
            IEnumerable<RatingKindEntity> expectedResult,
            TableContinuationToken expectedNext)
        {
            string hackName = "foo";

            var logger = new Mock<ILogger<RatingManagement>>();
            var cache = new Mock<ICacheProvider>();
            cache.Setup(c => c.GetOrAddAsync(It.Is<CacheEntry<IEnumerable<RatingKindEntity>>>(c => c.CacheKey == "RatingKind-foo"), default))
                .ReturnsAsync(allAwards);

            var ratingManagement = new RatingManagement(logger.Object)
            {
                Cache = cache.Object,
            };
            var result = await ratingManagement.ListPaginatedRatingKindsAsync(hackName, options, default);

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

        #region DeleteJudgeAsync
        [Test]
        public async Task DeleteJudgeAsync()
        {
            var logger = new Mock<ILogger<RatingManagement>>();
            var ratingKindTable = new Mock<IRatingKindTable>();
            ratingKindTable.Setup(j => j.DeleteAsync("hack", "kid", default));
            var storageContext = new Mock<IStorageContext>();
            storageContext.Setup(s => s.RatingKindTable).Returns(ratingKindTable.Object);
            var cache = new Mock<ICacheProvider>();
            cache.Setup(c => c.Remove("RatingKind-hack"));

            var ratingManagement = new RatingManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
                Cache = cache.Object,
            };
            await ratingManagement.DeleteRatingKindAsync("hack", "kid", default);

            Mock.VerifyAll(ratingKindTable, storageContext, cache);
            ratingKindTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            cache.VerifyNoOtherCalls();
        }
        #endregion

        #region CreateRatingAsync
        [Test]
        public async Task CreateRatingAsync()
        {
            var parameter = new Rating
            {
                hackathonName = "hack",
                description = "desc",
                judgeId = "jid",
                ratingKindId = "kid",
                score = 5,
                teamId = "tid",
            };

            var ratingTable = new Mock<IRatingTable> { };
            ratingTable.Setup(t => t.InsertAsync(It.Is<RatingEntity>(r =>
                  r.CreatedAt > DateTime.UtcNow.AddMinutes(-1) &&
                  r.Description == "desc" &&
                  r.HackathonName == "hack" &&
                  r.Id == "2f4291c6-d890-8fa1-316b-8c2b08256b25" &&
                  r.JudgeId == "jid" &&
                  r.RatingKindId == "kid" &&
                  r.Score == 5 &&
                  r.TeamId == "tid"
                ), default));
            var storageContext = new Mock<IStorageContext>();
            storageContext.Setup(s => s.RatingTable).Returns(ratingTable.Object);
            var logger = new Mock<ILogger<RatingManagement>>();

            var ratingManagement = new RatingManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
            };
            var result = await ratingManagement.CreateRatingAsync(parameter, default);

            Mock.VerifyAll(ratingTable, storageContext);
            ratingTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();

            Assert.AreEqual("desc", result.Description);
        }
        #endregion

        #region GetRatingAsync
        [Test]
        public async Task GetRatingAsync_ForCreate()
        {
            var entity = new RatingEntity { Description = "desc" };

            var ratingTable = new Mock<IRatingTable> { };
            ratingTable.Setup(t => t.RetrieveAsync("hack", "2f4291c6-d890-8fa1-316b-8c2b08256b25", default)).ReturnsAsync(entity);
            var storageContext = new Mock<IStorageContext>();
            storageContext.Setup(s => s.RatingTable).Returns(ratingTable.Object);
            var logger = new Mock<ILogger<RatingManagement>>();

            var ratingManagement = new RatingManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
            };
            var result = await ratingManagement.GetRatingAsync("hack", "jid", "tid", "kid", default);

            Mock.VerifyAll(ratingTable, storageContext);
            ratingTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();

            Assert.AreEqual("desc", result.Description);
        }
        #endregion
    }
}