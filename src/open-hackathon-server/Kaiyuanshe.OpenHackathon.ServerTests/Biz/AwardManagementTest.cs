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
    public class AwardManagementTest
    {
        [TestCase(null, null)]
        [TestCase(null, "")]
        [TestCase(null, " ")]
        [TestCase("", null)]
        [TestCase(" ", null)]
        public async Task GeAwardByIdAsync_Null(string hackName, string awardId)
        {
            var cancellationToken = CancellationToken.None;
            var logger = new Mock<ILogger<AwardManagement>>();
            AwardManagement awardManagement = new AwardManagement(logger.Object);
            var result = await awardManagement.GetAwardByIdAsync(hackName, awardId, cancellationToken);

            Mock.VerifyAll(logger);
            logger.VerifyNoOtherCalls();
            Assert.IsNull(result);
        }

        [Test]
        public async Task GeAwardByIdAsync_Succeeded()
        {
            string hackName = "Hack";
            string awardId = "aid";
            var cancellationToken = CancellationToken.None;
            AwardEntity teamEntity = new AwardEntity { Description = "desc" };

            var logger = new Mock<ILogger<AwardManagement>>();
            var awardTable = new Mock<IAwardTable>();
            awardTable.Setup(t => t.RetrieveAsync("hack", "aid", cancellationToken))
                .ReturnsAsync(teamEntity);
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.AwardTable).Returns(awardTable.Object);

            AwardManagement awardManagement = new AwardManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
            };
            var result = await awardManagement.GetAwardByIdAsync(hackName, awardId, cancellationToken);

            Mock.VerifyAll(logger, storageContext, awardTable);
            logger.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            awardTable.VerifyNoOtherCalls();
            Assert.AreEqual("desc", result.Description);
        }

        private static IEnumerable CreateAwardAsyncTestData()
        {
            // arg0: request
            // arg1: expected response

            // default quantity/target
            yield return new TestCaseData(
                    new Award { },
                    new AwardEntity { Quantity = 1, Target = AwardTarget.team }
                );

            // all
            yield return new TestCaseData(
                    new Award
                    {
                        quantity = 10,
                        target = AwardTarget.individual,
                        description = "desc",
                        name = "n",
                        pictures = new PictureInfo[]
                        {
                            new PictureInfo{ name="p1", description="d1", uri="u1" },
                            new PictureInfo{ name="p2", description="d2", uri="u2" },
                            new PictureInfo{ name="p3", description="d3", uri="u3" },
                        }
                    },
                    new AwardEntity
                    {
                        Quantity = 10,
                        Target = AwardTarget.individual,
                        Description = "desc",
                        Name = "n",
                        Pictures = new PictureInfo[]
                        {
                            new PictureInfo{ name="p1", description="d1", uri="u1" },
                            new PictureInfo{ name="p2", description="d2", uri="u2" },
                            new PictureInfo{ name="p3", description="d3", uri="u3" },
                        }
                    }
                );
        }

        [Test, TestCaseSource(nameof(CreateAwardAsyncTestData))]
        public async Task CreateAwardAsync(Award request, AwardEntity expectedEntity)
        {
            string hackName = "Hack";
            var cancellationToken = CancellationToken.None;

            var logger = new Mock<ILogger<AwardManagement>>();
            var awardTable = new Mock<IAwardTable>();
            awardTable.Setup(t => t.InsertAsync(It.IsAny<AwardEntity>(), cancellationToken));
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.AwardTable).Returns(awardTable.Object);
            var cache = new Mock<ICacheProvider>();
            cache.Setup(c => c.Remove("Award-Hack"));

            AwardManagement awardManagement = new AwardManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
                Cache = cache.Object,
            };
            var result = await awardManagement.CreateAwardAsync(hackName, request, cancellationToken);

            Mock.VerifyAll(logger, storageContext, awardTable, cache);
            logger.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            awardTable.VerifyNoOtherCalls();
            cache.VerifyNoOtherCalls();

            Assert.AreEqual(expectedEntity.Description, result.Description);
            Assert.AreEqual("hack", result.HackathonName);
            Assert.IsNotNull(result.Id);
            Assert.AreEqual(Guid.Empty.ToString().Length, result.Id.Length);
            Assert.AreEqual(expectedEntity.Name, result.Name);
            Assert.AreEqual("hack", result.PartitionKey);
            Assert.AreEqual(expectedEntity.Quantity, result.Quantity);
            Assert.AreEqual(expectedEntity.Target, result.Target);
            Assert.AreEqual(expectedEntity.Pictures?.Length, result.Pictures?.Length);
            for (int i = 0; i < result.Pictures?.Length; i++)
            {
                Assert.AreEqual(expectedEntity.Pictures[0].uri, result.Pictures[0].uri);
                Assert.AreEqual(expectedEntity.Pictures[0].name, result.Pictures[0].name);
                Assert.AreEqual(expectedEntity.Pictures[0].description, result.Pictures[0].description);
            }
        }

        #region UpdateAwardAsync
        private static IEnumerable UpdateAwardAsyncTestData()
        {
            // arg0: request
            // arg1: existing entity
            // arg2: expected updated entity

            // empty request
            yield return new TestCaseData(
                    new Award { },
                    new AwardEntity
                    {
                        Quantity = 10,
                        Target = AwardTarget.individual,
                        Description = "desc",
                        Name = "n",
                        Pictures = new PictureInfo[]
                        {
                            new PictureInfo{ name="p1", description="d1", uri="u1" },
                            new PictureInfo{ name="p2", description="d2", uri="u2" },
                            new PictureInfo{ name="p3", description="d3", uri="u3" },
                        }
                    },
                    new AwardEntity
                    {
                        Quantity = 10,
                        Target = AwardTarget.individual,
                        Description = "desc",
                        Name = "n",
                        Pictures = new PictureInfo[]
                        {
                            new PictureInfo{ name="p1", description="d1", uri="u1" },
                            new PictureInfo{ name="p2", description="d2", uri="u2" },
                            new PictureInfo{ name="p3", description="d3", uri="u3" },
                        }
                    }
                );

            // all updated
            yield return new TestCaseData(
                    new Award
                    {
                        name = "n2",
                        description = "d2",
                        quantity = 5,
                        target = AwardTarget.team,
                        pictures = new PictureInfo[]
                        {
                            new PictureInfo{ name="p4", description="d4", uri="u4" },
                        }
                    },
                    new AwardEntity
                    {
                        Quantity = 10,
                        Target = AwardTarget.individual,
                        Description = "desc",
                        Name = "n",
                        Pictures = new PictureInfo[]
                        {
                            new PictureInfo{ name="p1", description="d1", uri="u1" },
                            new PictureInfo{ name="p2", description="d2", uri="u2" },
                            new PictureInfo{ name="p3", description="d3", uri="u3" },
                        }
                    },
                    new AwardEntity
                    {
                        Quantity = 5,
                        Target = AwardTarget.team,
                        Description = "d2",
                        Name = "n2",
                        Pictures = new PictureInfo[]
                        {
                            new PictureInfo{ name="p4", description="d4", uri="u4" },
                        }
                    }
                );
        }

        [Test, TestCaseSource(nameof(UpdateAwardAsyncTestData))]
        public async Task UpdateAwardAsync(Award request, AwardEntity existing, AwardEntity expectedEntity)
        {
            var cancellationToken = CancellationToken.None;

            var logger = new Mock<ILogger<AwardManagement>>();
            var awardTable = new Mock<IAwardTable>();
            awardTable.Setup(t => t.MergeAsync(It.IsAny<AwardEntity>(), cancellationToken));
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.AwardTable).Returns(awardTable.Object);
            var cache = new Mock<ICacheProvider>();
            cache.Setup(c => c.Remove($"Award-{existing.HackathonName}"));

            AwardManagement awardManagement = new AwardManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
                Cache = cache.Object,
            };
            var result = await awardManagement.UpdateAwardAsync(existing, request, cancellationToken);

            Mock.VerifyAll(logger, storageContext, awardTable, cache);
            logger.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            awardTable.VerifyNoOtherCalls();
            cache.VerifyNoOtherCalls();

            Assert.AreEqual(expectedEntity.Description, result.Description);
            Assert.AreEqual(expectedEntity.Name, result.Name);
            Assert.AreEqual(expectedEntity.Quantity, result.Quantity);
            Assert.AreEqual(expectedEntity.Target, result.Target);
            Assert.AreEqual(expectedEntity.Pictures?.Length, result.Pictures?.Length);
            for (int i = 0; i < result.Pictures?.Length; i++)
            {
                Assert.AreEqual(expectedEntity.Pictures[0].uri, result.Pictures[0].uri);
                Assert.AreEqual(expectedEntity.Pictures[0].name, result.Pictures[0].name);
                Assert.AreEqual(expectedEntity.Pictures[0].description, result.Pictures[0].description);
            }
        }

        #endregion

        #region ListAwardsAsync
        [Test]
        public async Task ListAwardsAsync()
        {
            var cache = new Mock<ICacheProvider>();

            var awardManagement = new AwardManagement(null)
            {
                Cache = cache.Object,
            };
            await awardManagement.ListAwardsAsync("hack", default);

            cache.Verify(c => c.GetOrAddAsync(It.Is<CacheEntry<IEnumerable<AwardEntity>>>(e => e.AutoRefresh == true && e.CacheKey == "Award-hack"), default), Times.Once);
        }

        [Test]
        public async Task ListAwardsAsync2()
        {
            IEnumerable<AwardEntity> list = new List<AwardEntity>
            {
                new AwardEntity { RowKey = "rk" }
            };

            var awardTable = new Mock<IAwardTable>();
            awardTable.Setup(t => t.ListAllAwardsAsync("hack", default)).ReturnsAsync(list);
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.AwardTable).Returns(awardTable.Object);

            var awardManagement = new AwardManagement(null)
            {
                Cache = new DefaultCacheProvider(null),
                StorageContext = storageContext.Object,
            };
            var result = await awardManagement.ListAwardsAsync("hack", default);

            Mock.VerifyAll(awardTable, storageContext);
            awardTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();

            Assert.AreEqual(1, result.Count());
            Assert.AreEqual("rk", result.Single().Id);
        }
        #endregion

        #region ListPaginatedAwardsAsync

        private static IEnumerable ListPaginatedAwardsAsyncTestData()
        {
            var a1 = new AwardEntity
            {
                RowKey = "a1",
                CreatedAt = DateTime.UtcNow.AddDays(1),
            };
            var a2 = new AwardEntity
            {
                RowKey = "a1",
                CreatedAt = DateTime.UtcNow.AddDays(3),
            };
            var a3 = new AwardEntity
            {
                RowKey = "a1",
                CreatedAt = DateTime.UtcNow.AddDays(2),
            };
            var a4 = new AwardEntity
            {
                RowKey = "a1",
                CreatedAt = DateTime.UtcNow.AddDays(4),
            };

            // arg0: options
            // arg1: awards
            // arg2: expected result
            // arg3: expected Next

            // minimal
            yield return new TestCaseData(
                new AwardQueryOptions { },
                new List<AwardEntity> { a1, a2, a3, a4 },
                new List<AwardEntity> { a4, a2, a3, a1 },
                null
                );

            // top
            yield return new TestCaseData(
                new AwardQueryOptions { Top = 2 },
                new List<AwardEntity> { a1, a2, a3, a4 },
                new List<AwardEntity> { a4, a2, },
                new TableContinuationToken { NextPartitionKey = "2", NextRowKey = "nr" }
                );

            // paging
            yield return new TestCaseData(
                new AwardQueryOptions
                {
                    Top = 2,
                    TableContinuationToken = new TableContinuationToken
                    {
                        NextPartitionKey = "1",
                        NextRowKey = "nr"
                    }
                },
                new List<AwardEntity> { a1, a2, a3, a4 },
                new List<AwardEntity> { a2, a3, },
                new TableContinuationToken { NextPartitionKey = "3", NextRowKey = "nr" }
                );
        }

        [Test, TestCaseSource(nameof(ListPaginatedAwardsAsyncTestData))]
        public async Task ListPaginatedAwardsAsync_Options(
            AwardQueryOptions options,
            IEnumerable<AwardEntity> allAwards,
            IEnumerable<AwardEntity> expectedResult,
            TableContinuationToken expectedNext)
        {
            string hackName = "foo";

            var logger = new Mock<ILogger<AwardManagement>>();
            var cache = new Mock<ICacheProvider>();
            cache.Setup(c => c.GetOrAddAsync(It.Is<CacheEntry<IEnumerable<AwardEntity>>>(c => c.CacheKey == "Award-foo"), default))
                .ReturnsAsync(allAwards);

            var awardManagement = new AwardManagement(logger.Object)
            {
                Cache = cache.Object,
            };
            var result = await awardManagement.ListPaginatedAwardsAsync(hackName, options, default);

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

        #region DeleteAwardAsync
        [Test]
        public async Task DeleteAwardAsync()
        {
            var cancellationToken = CancellationToken.None;
            AwardEntity award = new AwardEntity
            {
                PartitionKey = "pk",
                RowKey = "rk",
            };

            var logger = new Mock<ILogger<AwardManagement>>();
            var awardTable = new Mock<IAwardTable>();
            awardTable.Setup(t => t.DeleteAsync("pk", "rk", cancellationToken));
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.AwardTable).Returns(awardTable.Object);
            var cache = new Mock<ICacheProvider>();
            cache.Setup(c => c.Remove("Award-pk"));

            AwardManagement awardManagement = new AwardManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
                Cache = cache.Object,
            };
            await awardManagement.DeleteAwardAsync(award, cancellationToken);

            Mock.VerifyAll(logger, storageContext, awardTable, cache);
            logger.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            awardTable.VerifyNoOtherCalls();
            cache.VerifyNoOtherCalls();
        }
        #endregion

        #region CreateOrUpdateAssignmentAsync
        [Test]
        public async Task CreateOrUpdateAssignmentAsync_Create()
        {
            var assignments = new List<AwardAssignmentEntity>
            {
                new AwardAssignmentEntity
                {
                    AssigneeId = "other"
                }
            };
            var request = new AwardAssignment
            {
                assigneeId = "tid",
                awardId = "award",
                description = "desc",
                hackathonName = "hack",
            };

            var logger = new Mock<ILogger<AwardManagement>>();
            var awardAssignmentTable = new Mock<IAwardAssignmentTable>();
            awardAssignmentTable.Setup(t => t.ListByAwardAsync("hack", "award", default)).ReturnsAsync(assignments);
            awardAssignmentTable.Setup(t => t.InsertAsync(It.IsAny<AwardAssignmentEntity>(), default));
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.AwardAssignmentTable).Returns(awardAssignmentTable.Object);

            AwardManagement awardManagement = new AwardManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
            };
            var result = await awardManagement.CreateOrUpdateAssignmentAsync(request, default);

            Mock.VerifyAll(logger, storageContext, awardAssignmentTable);
            logger.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            awardAssignmentTable.Verify(t => t.InsertAsync(It.Is<AwardAssignmentEntity>(
                a => a.AssigneeId == "tid"
                && a.AwardId == "award"
                && a.Description == "desc"
                && a.HackathonName == "hack"
                && !string.IsNullOrWhiteSpace(a.AssignmentId)), default));
            awardAssignmentTable.VerifyNoOtherCalls();

            Assert.AreEqual("tid", result.AssigneeId);
            Assert.AreEqual("award", result.AwardId);
            Assert.AreEqual("desc", result.Description);
            Assert.AreEqual("hack", result.HackathonName);
            Assert.IsFalse(string.IsNullOrWhiteSpace(result.AssignmentId));
        }

        [Test]
        public async Task CreateOrUpdateAssignmentAsync_Update()
        {
            var assignments = new List<AwardAssignmentEntity>
            {
                new AwardAssignmentEntity
                {
                    AssigneeId = "tid",
                    Description = "desc"
                }
            };
            var request = new AwardAssignment
            {
                assigneeId = "tid",
                awardId = "award",
                description = "updated desc",
                hackathonName = "hack",
            };

            var logger = new Mock<ILogger<AwardManagement>>();
            var awardAssignmentTable = new Mock<IAwardAssignmentTable>();
            awardAssignmentTable.Setup(t => t.ListByAwardAsync("hack", "award", default)).ReturnsAsync(assignments);
            awardAssignmentTable.Setup(t => t.MergeAsync(It.IsAny<AwardAssignmentEntity>(), default));
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.AwardAssignmentTable).Returns(awardAssignmentTable.Object);

            AwardManagement awardManagement = new AwardManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
            };
            var result = await awardManagement.CreateOrUpdateAssignmentAsync(request, default);

            Mock.VerifyAll(logger, storageContext, awardAssignmentTable);
            logger.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            awardAssignmentTable.Verify(t => t.MergeAsync(It.Is<AwardAssignmentEntity>(a => a.Description == "updated desc"), default));
            awardAssignmentTable.VerifyNoOtherCalls();

            Assert.AreEqual("tid", result.AssigneeId);
            Assert.AreEqual("updated desc", result.Description);
        }
        #endregion
    }
}
