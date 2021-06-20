using Kaiyuanshe.OpenHackathon.Server.Auth;
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
using System.Security.Claims;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Biz
{
    [TestFixture]
    public class HackathonManagementTest
    {
        #region CreateHackathonAsyncTest
        [Test]
        public async Task CreateHackathonAsyncTest()
        {
            // input
            var request = new Hackathon
            {
                name = "test",
                location = "loc",
                eventStartedAt = DateTime.UtcNow,
                tags = new string[] { "a", "b", "c" },
                banners = new PictureInfo[] { new PictureInfo { Name = "pn", Description = "pd", Uri = "pu" } },
                creatorId = "uid"
            };
            CancellationToken cancellationToken = CancellationToken.None;

            // capture
            HackathonEntity hackInserted = null;
            HackathonAdmin adminCaptured = null;

            // mock
            var hackathonTable = new Mock<IHackathonTable>();
            hackathonTable.Setup(p => p.InsertAsync(It.IsAny<HackathonEntity>(), cancellationToken))
                .Callback<HackathonEntity, CancellationToken>((h, c) => { hackInserted = h; });
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.HackathonTable).Returns(hackathonTable.Object);
            var cache = new Mock<ICacheProvider>();
            cache.Setup(c => c.Remove(HackathonManagement.cacheKeyForAllHackathon));
            var hackathonAdminManagement = new Mock<IHackathonAdminManagement>();
            hackathonAdminManagement.Setup(a => a.CreateAdminAsync(It.IsAny<HackathonAdmin>(), cancellationToken))
                .Callback<HackathonAdmin, CancellationToken>((a, ct) =>
                {
                    adminCaptured = a;
                });

            // test
            var hackathonManager = new HackathonManagement(null)
            {
                StorageContext = storageContext.Object,
                HackathonAdminManagement = hackathonAdminManagement.Object,
                Cache = cache.Object,
            };
            var result = await hackathonManager.CreateHackathonAsync(request, CancellationToken.None);

            // verify
            Mock.VerifyAll(hackathonTable, hackathonAdminManagement, storageContext, cache);
            hackathonTable.VerifyNoOtherCalls();
            hackathonAdminManagement.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            cache.VerifyNoOtherCalls();

            Assert.AreEqual("loc", result.Location);
            Assert.AreEqual("test", result.PartitionKey);
            Assert.AreEqual("uid", result.CreatorId);
            Assert.AreEqual(string.Empty, result.RowKey);
            Assert.IsTrue(result.EventStartedAt.HasValue);
            Assert.IsFalse(result.EventEndedAt.HasValue);

            Assert.AreEqual("loc", hackInserted.Location);
            Assert.AreEqual("uid", hackInserted.CreatorId);
            Assert.AreEqual(new string[] { "a", "b", "c" }, hackInserted.Tags);
            Assert.AreEqual(1, hackInserted.Banners.Length);
            Assert.AreEqual("pn", hackInserted.Banners[0].Name);
            Assert.AreEqual("pd", hackInserted.Banners[0].Description);
            Assert.AreEqual("pu", hackInserted.Banners[0].Uri);

            Assert.AreEqual("test", adminCaptured.hackathonName);
            Assert.AreEqual("uid", adminCaptured.userId);
        }
        #endregion

        [TestCase(HackathonStatus.planning, HackathonStatus.planning)]
        [TestCase(HackathonStatus.pendingApproval, HackathonStatus.pendingApproval)]
        [TestCase(HackathonStatus.online, HackathonStatus.online)]
        [TestCase(HackathonStatus.offline, HackathonStatus.offline)]
        public async Task UpdateHackathonStatusAsync_Skip(HackathonStatus origin, HackathonStatus target)
        {
            CancellationToken cancellationToken = CancellationToken.None;
            HackathonEntity hackathonEntity = new HackathonEntity { Status = origin };

            var hackathonManagement = new HackathonManagement(null)
            {
            };
            var updated = await hackathonManagement.UpdateHackathonStatusAsync(hackathonEntity, target, cancellationToken);
            Assert.AreEqual(target, updated.Status);
            Assert.IsNull(await hackathonManagement.UpdateHackathonStatusAsync(null, target, cancellationToken));
        }

        [TestCase(HackathonStatus.planning, HackathonStatus.pendingApproval)]
        [TestCase(HackathonStatus.planning, HackathonStatus.online)]
        [TestCase(HackathonStatus.planning, HackathonStatus.offline)]
        [TestCase(HackathonStatus.pendingApproval, HackathonStatus.online)]
        [TestCase(HackathonStatus.pendingApproval, HackathonStatus.offline)]
        [TestCase(HackathonStatus.online, HackathonStatus.offline)]
        public async Task UpdateHackathonStatusAsync_Succeeded(HackathonStatus origin, HackathonStatus target)
        {
            CancellationToken cancellationToken = CancellationToken.None;
            HackathonEntity hackathonEntity = new HackathonEntity { Status = origin };

            HackathonEntity captured = null;
            var hackathonTable = new Mock<IHackathonTable>();
            hackathonTable.Setup(p => p.MergeAsync(It.IsAny<HackathonEntity>(), cancellationToken))
                .Callback<HackathonEntity, CancellationToken>((entity, ct) =>
                {
                    captured = entity;
                });
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.HackathonTable).Returns(hackathonTable.Object);

            var cache = new Mock<ICacheProvider>();
            cache.Setup(c => c.Remove(HackathonManagement.cacheKeyForAllHackathon));

            // test
            var hackathonManagement = new HackathonManagement(null)
            {
                StorageContext = storageContext.Object,
                Cache = cache.Object,
            };
            var updated = await hackathonManagement.UpdateHackathonStatusAsync(hackathonEntity, target, cancellationToken);

            Mock.VerifyAll(storageContext, hackathonTable, cache);
            hackathonTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            cache.VerifyNoOtherCalls();

            Assert.AreEqual(target, captured.Status);
            Assert.AreEqual(target, updated.Status);
        }

        [Test]
        public async Task GetHackathonEntityByNameAsyncTest()
        {
            string name = "test";
            var entity = new HackathonEntity
            {
                Location = "loc"
            };

            var hackathonTable = new Mock<IHackathonTable>();
            hackathonTable.Setup(p => p.RetrieveAsync(name, string.Empty, CancellationToken.None))
                .ReturnsAsync(entity);

            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.HackathonTable).Returns(hackathonTable.Object);

            var hackathonManager = new HackathonManagement(null);
            hackathonManager.StorageContext = storageContext.Object;
            var result = await hackathonManager.GetHackathonEntityByNameAsync(name, CancellationToken.None);

            Mock.VerifyAll();
            hackathonTable.Verify(p => p.RetrieveAsync(name, string.Empty, CancellationToken.None), Times.Once);
            hackathonTable.VerifyNoOtherCalls();

            storageContext.VerifyGet(p => p.HackathonTable, Times.Once);
            storageContext.VerifyNoOtherCalls();

            Assert.AreEqual("loc", result.Location);
        }

        #region ListPaginatedHackathonsAsync
        private static IEnumerable ListPaginatedHackathonsAsyncTestData()
        {
            var offline = new HackathonEntity { Status = HackathonStatus.offline };
            var planning = new HackathonEntity { Status = HackathonStatus.planning };
            var pendingApproval = new HackathonEntity { Status = HackathonStatus.pendingApproval };

            var h1 = new HackathonEntity
            {
                Status = HackathonStatus.online,
                PartitionKey = "h1 search",
                CreatedAt = DateTime.Now.AddDays(1),
                Timestamp = DateTimeOffset.Now.AddDays(1),
            };
            var h2 = new HackathonEntity
            {
                Status = HackathonStatus.online,
                PartitionKey = "h2",
                DisplayName = "asearch DisplayName",
                CreatedAt = DateTime.Now.AddDays(2),
                Timestamp = DateTimeOffset.Now.AddDays(-1),
            };
            var h3 = new HackathonEntity
            {
                Status = HackathonStatus.online,
                PartitionKey = "h3",
                Detail = "search Detail",
                CreatedAt = DateTime.Now.AddDays(3),
                Timestamp = DateTimeOffset.Now.AddDays(2),
            };
            var h4 = new HackathonEntity
            {
                Status = HackathonStatus.online,
                PartitionKey = "searc h4",
                CreatedAt = DateTime.Now.AddDays(4),
                Timestamp = DateTimeOffset.Now.AddDays(-2),
            };

            // arg0: all hackathons
            // arg1: options
            // arg2: expected result
            // arg3: expected next

            // empty
            yield return new TestCaseData(
                new Dictionary<string, HackathonEntity>
                {
                    { "offline", offline },
                    { "planning", planning},
                    { "pendingApproval", pendingApproval }
                },
                new HackathonQueryOptions { },
                new List<HackathonEntity>
                {
                },
                null
                );

            // search and default ordering
            yield return new TestCaseData(
                new Dictionary<string, HackathonEntity>
                {
                    { "offline", offline },
                    { "h1", h1 },
                    { "h2", h2 },
                    { "h3", h3 },
                    { "h4", h4 }
                },
                new HackathonQueryOptions { Search = "search" },
                new List<HackathonEntity>
                {
                    h3, h2, h1
                },
                null
                );

            // ordering by updateBy
            yield return new TestCaseData(
                new Dictionary<string, HackathonEntity>
                {
                    { "offline", offline },
                    { "h1", h1 },
                    { "h2", h2 },
                    { "h3", h3 },
                    { "h4", h4 }
                },
                new HackathonQueryOptions { OrderBy = HackathonOrderBy.updatedAt },
                new List<HackathonEntity>
                {
                    h3, h1, h2, h4
                },
                null
                );

            // paging
            yield return new TestCaseData(
                new Dictionary<string, HackathonEntity>
                {
                    { "offline", offline },
                    { "h1", h1 },
                    { "h2", h2 },
                    { "h3", h3 },
                    { "h4", h4 }
                },
                new HackathonQueryOptions
                {
                    TableContinuationToken = new TableContinuationToken
                    {
                        NextPartitionKey = "3"
                    }
                },
                new List<HackathonEntity>
                {
                    h1
                },
                null
                );

            // unknown paging para
            yield return new TestCaseData(
                new Dictionary<string, HackathonEntity>
                {
                    { "offline", offline },
                    { "h1", h1 },
                    { "h2", h2 },
                    { "h3", h3 },
                    { "h4", h4 }
                },
                new HackathonQueryOptions
                {
                    TableContinuationToken = new TableContinuationToken
                    {
                        NextPartitionKey = "not an int"
                    }
                },
                new List<HackathonEntity>
                {
                    h4, h3, h2, h1
                },
                null
                );

            // top
            yield return new TestCaseData(
                new Dictionary<string, HackathonEntity>
                {
                    { "offline", offline },
                    { "h1", h1 },
                    { "h2", h2 },
                    { "h3", h3 },
                    { "h4", h4 }
                },
                new HackathonQueryOptions
                {
                    Top = 3
                },
                new List<HackathonEntity>
                {
                    h4, h3, h2
                },
                new TableContinuationToken
                {
                    NextPartitionKey = "3",
                    NextRowKey = "nr"
                }
                );

            // top + paging
            yield return new TestCaseData(
                new Dictionary<string, HackathonEntity>
                {
                    { "offline", offline },
                    { "h1", h1 },
                    { "h2", h2 },
                    { "h3", h3 },
                    { "h4", h4 }
                },
                new HackathonQueryOptions
                {
                    TableContinuationToken = new TableContinuationToken
                    {
                        NextPartitionKey = "1"
                    },
                    Top = 2
                },
                new List<HackathonEntity>
                {
                    h3, h2
                },
                new TableContinuationToken
                {
                    NextPartitionKey = "3",
                    NextRowKey = "nr"
                }
                );
        }

        [Test, TestCaseSource(nameof(ListPaginatedHackathonsAsyncTestData))]
        public async Task ListPaginatedHackathonsAsync_Options(
            Dictionary<string, HackathonEntity> allHackathons,
            HackathonQueryOptions options,
            List<HackathonEntity> expectedResult,
            TableContinuationToken expectedNext)
        {
            CancellationToken cancellationToken = CancellationToken.None;

            var logger = new Mock<ILogger<HackathonManagement>>();
            var cache = new Mock<ICacheProvider>();
            cache.Setup(c => c.GetOrAddAsync(It.IsAny<CacheEntry<Dictionary<string, HackathonEntity>>>(), cancellationToken))
                .ReturnsAsync(allHackathons);

            var hackathonManagement = new HackathonManagement(logger.Object)
            {
                Cache = cache.Object,
            };
            var result = await hackathonManagement.ListPaginatedHackathonsAsync(options, cancellationToken);

            Mock.VerifyAll(cache);
            cache.VerifyNoOtherCalls();

            if (expectedNext == null)
                Assert.IsNull(options.Next);
            else
            {
                Assert.AreEqual(options.Next.NextPartitionKey, expectedNext.NextPartitionKey);
                Assert.AreEqual(options.Next.NextRowKey, expectedNext.NextRowKey);
            }
            Assert.AreEqual(result.Count(), expectedResult.Count());
            for (int i = 0; i < result.Count(); i++)
            {
                Assert.AreEqual(result.ElementAt(i).Name, expectedResult[i].Name);
                Assert.AreEqual(result.ElementAt(i).DisplayName, expectedResult[i].DisplayName);
                Assert.AreEqual(result.ElementAt(i).Detail, expectedResult[i].Detail);
                Assert.AreEqual(result.ElementAt(i).CreatedAt, expectedResult[i].CreatedAt);
                Assert.AreEqual(result.ElementAt(i).Timestamp, expectedResult[i].Timestamp);
                Assert.AreEqual(result.ElementAt(i).Status, expectedResult[i].Status);
            }
        }
        #endregion

        #region ListPaginatedMyManagableHackathonsAsync
        private static IEnumerable ListPaginatedMyManagableHackathonsAsyncTestData()
        {
            var h1 = new HackathonEntity
            {
                PartitionKey = "h1",
                CreatedAt = DateTime.Now.AddDays(1),
            };
            var h2 = new HackathonEntity
            {
                PartitionKey = "h2",
                CreatedAt = DateTime.Now.AddDays(2),
            };
            var h3 = new HackathonEntity
            {
                PartitionKey = "h3",
                CreatedAt = DateTime.Now.AddDays(3),
            };
            var h4 = new HackathonEntity
            {
                PartitionKey = "h4",
                CreatedAt = DateTime.Now.AddDays(4),
            };

            var a0 = new HackathonAdminEntity { RowKey = "uid" };
            var a1 = new HackathonAdminEntity { RowKey = "a1" };
            var a2 = new HackathonAdminEntity { RowKey = "a2" };

            // arg0: user
            // arg1: all hackathons
            // arg2: admins
            // arg3: expected result

            // empty user
            yield return new TestCaseData(
                null,
                new Dictionary<string, HackathonEntity>
                {
                    { "h1", h1 },
                    { "h2", h2 },
                    { "h3", h3 },
                    { "h4", h4 }
                },
                null,
                new List<HackathonEntity>()
                );

            // Platform Admin
            yield return new TestCaseData(
                new ClaimsPrincipal(
                    new ClaimsIdentity(new List<Claim>
                    {
                        new Claim(AuthConstant.ClaimType.PlatformAdministrator, "foo")
                    })
                ),
                new Dictionary<string, HackathonEntity>
                {
                    { "h1", h1 },
                    { "h2", h2 },
                    { "h3", h3 },
                    { "h4", h4 }
                },
                null,
                new List<HackathonEntity>
                {
                    h4, h3, h2, h1
                }
                );

            // normal user
            yield return new TestCaseData(
                new ClaimsPrincipal(
                    new ClaimsIdentity(new List<Claim>
                    {
                        new Claim(AuthConstant.ClaimType.UserId, "uid")
                    })
                ),
                new Dictionary<string, HackathonEntity>
                {
                    { "h1", h1 },
                    { "h2", h2 },
                    { "h3", h3 },
                    { "h4", h4 }
                },
                new Dictionary<string, List<HackathonAdminEntity>>
                {
                    { "h1", new List<HackathonAdminEntity> { } },
                    { "h2", new List<HackathonAdminEntity> { a0 } },
                    { "h3", new List<HackathonAdminEntity> { a1, a2 } },
                    { "h4", new List<HackathonAdminEntity> { a0, a1 } }
                },
                new List<HackathonEntity>
                {
                    h4, h2
                }
                );
        }

        [Test, TestCaseSource(nameof(ListPaginatedMyManagableHackathonsAsyncTestData))]
        public async Task ListPaginatedMyManagableHackathonsAsync(
            ClaimsPrincipal user,
            Dictionary<string, HackathonEntity> allHackathons,
            Dictionary<string, List<HackathonAdminEntity>> admins,
            List<HackathonEntity> expectedResult)
        {
            CancellationToken cancellationToken = CancellationToken.None;
            var options = new HackathonQueryOptions
            {
                OrderBy = HackathonOrderBy.createdAt,
            };

            var logger = new Mock<ILogger<HackathonManagement>>();
            var cache = new Mock<ICacheProvider>();
            if (user != null)
            {
                cache.Setup(c => c.GetOrAddAsync(It.IsAny<CacheEntry<Dictionary<string, HackathonEntity>>>(), cancellationToken))
                    .ReturnsAsync(allHackathons);
            }
            var hackathonAdminManagement = new Mock<IHackathonAdminManagement>();
            if (admins != null)
            {
                foreach (var item in admins)
                {
                    hackathonAdminManagement.Setup(p => p.ListHackathonAdminAsync(item.Key, cancellationToken))
                        .ReturnsAsync(item.Value);
                }
            }

            var hackathonManagement = new HackathonManagement(logger.Object)
            {
                Cache = cache.Object,
                HackathonAdminManagement = hackathonAdminManagement.Object,
            };
            var result = await hackathonManagement.ListPaginatedMyManagableHackathonsAsync(user, options, cancellationToken);

            Mock.VerifyAll(cache, hackathonAdminManagement);
            cache.VerifyNoOtherCalls();
            hackathonAdminManagement.VerifyNoOtherCalls();

            Assert.AreEqual(result.Count(), expectedResult.Count());
            for (int i = 0; i < result.Count(); i++)
            {
                Assert.AreEqual(result.ElementAt(i).Name, expectedResult[i].Name);
                Assert.AreEqual(result.ElementAt(i).CreatedAt, expectedResult[i].CreatedAt);
            }
        }
        #endregion

        #region ListAllHackathonsAsync
        [Test]
        public async Task ListAllHackathonsAsync()
        {
            CancellationToken cancellationToken = CancellationToken.None;
            Dictionary<string, HackathonEntity> data = new Dictionary<string, HackathonEntity>
            {
                { "test", new HackathonEntity{ } }
            };

            var logger = new Mock<ILogger<HackathonManagement>>();
            var hackathonTable = new Mock<IHackathonTable>();
            hackathonTable.Setup(p => p.ListAllHackathonsAsync(cancellationToken)).ReturnsAsync(data);
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.HackathonTable).Returns(hackathonTable.Object);

            var hackathonManagement = new HackathonManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
                Cache = new DefaultCacheProvider(null),
            };
            var result = await hackathonManagement.ListAllHackathonsAsync(cancellationToken);

            Mock.VerifyAll(hackathonTable, storageContext);
            hackathonTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            Assert.AreEqual(1, result.Count);
        }
        #endregion

        [Test]
        public async Task UpdateHackathonAsyncTest()
        {
            string name = "test";
            var entity = new HackathonEntity
            {
                Location = "loc"
            };
            var request = new Hackathon
            {
                name = name,
            };

            var hackathonTable = new Mock<IHackathonTable>();
            hackathonTable.Setup(p => p.RetrieveAndMergeAsync(name, string.Empty, It.IsAny<Action<HackathonEntity>>(), CancellationToken.None))
                .ReturnsAsync(default(TableResult));
            hackathonTable.Setup(p => p.RetrieveAsync(name, string.Empty, CancellationToken.None))
                .ReturnsAsync(entity);

            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.HackathonTable).Returns(hackathonTable.Object);

            var cache = new Mock<ICacheProvider>();
            cache.Setup(c => c.Remove(HackathonManagement.cacheKeyForAllHackathon));

            // test
            var hackathonManager = new HackathonManagement(null)
            {
                StorageContext = storageContext.Object,
                Cache = cache.Object,
            };
            var result = await hackathonManager.UpdateHackathonAsync(request, CancellationToken.None);

            Mock.VerifyAll(hackathonTable, storageContext, cache);
            hackathonTable.Verify(p => p.RetrieveAndMergeAsync(name, string.Empty, It.IsAny<Action<HackathonEntity>>(), CancellationToken.None), Times.Once);
            hackathonTable.Verify(p => p.RetrieveAsync(name, string.Empty, CancellationToken.None), Times.Once);
            hackathonTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            cache.VerifyNoOtherCalls();

            storageContext.VerifyGet(p => p.HackathonTable, Times.Exactly(2));
            storageContext.VerifyNoOtherCalls();

            Assert.AreEqual("loc", result.Location);
        }

        [Test]
        public async Task EnrollAsyncTest_Enrolled()
        {
            HackathonEntity hackathon = new HackathonEntity
            {
                PartitionKey = "hack"
            };
            string userId = "uid";
            EnrollmentEntity participant = new EnrollmentEntity();
            CancellationToken cancellation = CancellationToken.None;
            var logger = new Mock<ILogger<HackathonManagement>>();

            var enrollmentTable = new Mock<IEnrollmentTable>();
            enrollmentTable.Setup(p => p.RetrieveAsync("hack", userId, cancellation)).ReturnsAsync(participant);
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.EnrollmentTable).Returns(enrollmentTable.Object);

            var hackathonManagement = new HackathonManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
            };
            await hackathonManagement.EnrollAsync(hackathon, userId, cancellation);

            Mock.VerifyAll(storageContext, enrollmentTable);
            enrollmentTable.VerifyNoOtherCalls();
        }

        [TestCase(false, EnrollmentStatus.pendingApproval)]
        [TestCase(true, EnrollmentStatus.approved)]
        public async Task EnrollAsyncTest_Insert(bool autoApprove, EnrollmentStatus targetStatus)
        {
            HackathonEntity hackathon = new HackathonEntity
            {
                PartitionKey = "hack",
                AutoApprove = autoApprove,
            };
            string userId = "uid";
            EnrollmentEntity participant = null;
            CancellationToken cancellation = CancellationToken.None;
            var logger = new Mock<ILogger<HackathonManagement>>();

            var participantTable = new Mock<IEnrollmentTable>();
            participantTable.Setup(p => p.RetrieveAsync("hack", userId, cancellation)).ReturnsAsync(participant);
            participantTable.Setup(p => p.InsertAsync(It.IsAny<EnrollmentEntity>(), cancellation))
                .Callback<EnrollmentEntity, CancellationToken>((p, c) =>
                {
                    participant = p;
                });
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.EnrollmentTable).Returns(participantTable.Object);

            var hackathonManagement = new HackathonManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
            };
            await hackathonManagement.EnrollAsync(hackathon, userId, cancellation);

            Mock.VerifyAll(storageContext, participantTable);
            participantTable.VerifyNoOtherCalls();
            Assert.AreEqual(targetStatus, participant.Status);
        }

        [Test]
        public async Task EnrollUpdateStatusAsyncTest_Null()
        {
            EnrollmentEntity participant = null;
            CancellationToken cancellation = CancellationToken.None;
            var logger = new Mock<ILogger<HackathonManagement>>();

            var hackathonManagement = new HackathonManagement(logger.Object);
            await hackathonManagement.UpdateEnrollmentStatusAsync(participant, EnrollmentStatus.approved, cancellation);

            Mock.VerifyAll(logger);
            logger.VerifyNoOtherCalls();
            Assert.IsNull(participant);
        }

        [TestCase(EnrollmentStatus.approved)]
        [TestCase(EnrollmentStatus.rejected)]
        public async Task EnrollUpdateStatusAsyncTest_Updated(EnrollmentStatus parameter)
        {
            EnrollmentEntity participant = new EnrollmentEntity();
            CancellationToken cancellation = CancellationToken.None;
            var logger = new Mock<ILogger<HackathonManagement>>();

            EnrollmentEntity captured = null;
            var enrollmentTable = new Mock<IEnrollmentTable>();
            enrollmentTable.Setup(p => p.MergeAsync(It.IsAny<EnrollmentEntity>(), cancellation))
                .Callback<EnrollmentEntity, CancellationToken>((p, c) =>
                {
                    captured = p;
                });

            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.EnrollmentTable).Returns(enrollmentTable.Object);

            var hackathonManagement = new HackathonManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
            };
            await hackathonManagement.UpdateEnrollmentStatusAsync(participant, parameter, cancellation);

            Mock.VerifyAll(storageContext, enrollmentTable, logger);
            enrollmentTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            Assert.IsNotNull(captured);
            Assert.AreEqual(parameter, captured.Status);
            Assert.AreEqual(parameter, participant.Status);
        }

        [TestCase(null, null)]
        [TestCase(null, "uid")]
        [TestCase("hack", null)]
        public async Task GetEnrollmentAsyncTest_NotFound(string hackathon, string userId)
        {
            var hackathonManagement = new HackathonManagement(null);
            var enrollment = await hackathonManagement.GetEnrollmentAsync(hackathon, userId);
            Assert.IsNull(enrollment);
        }

        [Test]
        public async Task GetEnrollmentAsyncTest_Succeeded()
        {
            EnrollmentEntity participant = new EnrollmentEntity { Status = EnrollmentStatus.rejected };
            CancellationToken cancellation = CancellationToken.None;
            var logger = new Mock<ILogger<HackathonManagement>>();

            var enrollmentTable = new Mock<IEnrollmentTable>();
            enrollmentTable.Setup(p => p.RetrieveAsync("hack", "uid", cancellation)).ReturnsAsync(participant);
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.EnrollmentTable).Returns(enrollmentTable.Object);

            var hackathonManagement = new HackathonManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
            };

            var enrollment = await hackathonManagement.GetEnrollmentAsync("Hack", "UID", cancellation);
            Assert.IsNotNull(enrollment);
            Assert.AreEqual(EnrollmentStatus.rejected, enrollment.Status);
        }

        [Test]
        public async Task ListPaginatedEnrollmentsAsync_NoOptions()
        {
            string hackName = "foo";
            EnrollmentQueryOptions options = null;
            CancellationToken cancellationToken = CancellationToken.None;
            var entities = MockHelper.CreateTableQuerySegment<EnrollmentEntity>(
                 new List<EnrollmentEntity>
                 {
                     new EnrollmentEntity{  PartitionKey="pk" }
                 },
                 new TableContinuationToken { NextPartitionKey = "np", NextRowKey = "nr" }
                );

            TableQuery<EnrollmentEntity> tableQueryCaptured = null;
            TableContinuationToken tableContinuationTokenCapatured = null;

            var logger = new Mock<ILogger<HackathonManagement>>();
            var enrollmentTable = new Mock<IEnrollmentTable>();
            enrollmentTable.Setup(p => p.ExecuteQuerySegmentedAsync(It.IsAny<TableQuery<EnrollmentEntity>>(), It.IsAny<TableContinuationToken>(), cancellationToken))
                .Callback<TableQuery<EnrollmentEntity>, TableContinuationToken, CancellationToken>((query, c, _) =>
                {
                    tableQueryCaptured = query;
                    tableContinuationTokenCapatured = c;
                })
                .ReturnsAsync(entities);
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.EnrollmentTable).Returns(enrollmentTable.Object);

            var hackathonManagement = new HackathonManagement(logger.Object)
            {
                StorageContext = storageContext.Object
            };
            var segment = await hackathonManagement.ListPaginatedEnrollmentsAsync(hackName, options, cancellationToken);

            Mock.VerifyAll(enrollmentTable, storageContext);
            enrollmentTable.VerifyNoOtherCalls();
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
        public async Task ListPaginatedEnrollmentsAsync_Options(int topInPara, int expectedTop)
        {
            string hackName = "foo";
            EnrollmentQueryOptions options = new EnrollmentQueryOptions
            {
                TableContinuationToken = new TableContinuationToken { NextPartitionKey = "np", NextRowKey = "nr" },
                Top = topInPara,
                Status = EnrollmentStatus.approved
            };
            CancellationToken cancellationToken = CancellationToken.None;
            var entities = MockHelper.CreateTableQuerySegment<EnrollmentEntity>(
                 new List<EnrollmentEntity>
                 {
                     new EnrollmentEntity{  PartitionKey="pk" }
                 },
                 new TableContinuationToken { NextPartitionKey = "np2", NextRowKey = "nr2" }
                );

            TableQuery<EnrollmentEntity> tableQueryCaptured = null;
            TableContinuationToken tableContinuationTokenCapatured = null;

            var logger = new Mock<ILogger<HackathonManagement>>();
            var enrollmentTable = new Mock<IEnrollmentTable>();
            enrollmentTable.Setup(p => p.ExecuteQuerySegmentedAsync(It.IsAny<TableQuery<EnrollmentEntity>>(), It.IsAny<TableContinuationToken>(), cancellationToken))
                .Callback<TableQuery<EnrollmentEntity>, TableContinuationToken, CancellationToken>((query, c, _) =>
                {
                    tableQueryCaptured = query;
                    tableContinuationTokenCapatured = c;
                })
                .ReturnsAsync(entities);
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.EnrollmentTable).Returns(enrollmentTable.Object);

            var hackathonManagement = new HackathonManagement(logger.Object)
            {
                StorageContext = storageContext.Object
            };
            var segment = await hackathonManagement.ListPaginatedEnrollmentsAsync(hackName, options, cancellationToken);

            Mock.VerifyAll(enrollmentTable, storageContext);
            enrollmentTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();

            Assert.AreEqual(1, segment.Count());
            Assert.AreEqual("pk", segment.First().HackathonName);
            Assert.AreEqual("np2", segment.ContinuationToken.NextPartitionKey);
            Assert.AreEqual("nr2", segment.ContinuationToken.NextRowKey);
            Assert.AreEqual("np", tableContinuationTokenCapatured.NextPartitionKey);
            Assert.AreEqual("nr", tableContinuationTokenCapatured.NextRowKey);
            Assert.AreEqual("(PartitionKey eq 'foo') and (Status eq 2)", tableQueryCaptured.FilterString);
            Assert.AreEqual(expectedTop, tableQueryCaptured.TakeCount.Value);
        }
    }
}
