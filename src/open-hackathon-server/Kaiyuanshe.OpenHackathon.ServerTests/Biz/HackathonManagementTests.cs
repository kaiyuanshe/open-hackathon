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
    public class HackathonManagementTests
    {
        #region CanCreateHackathonAsync
        private static IEnumerable CanCreateHackathonAsyncTestData()
        {
            // arg0: entities
            // arg1: expectedResult

            // >3 in 1 day
            yield return new TestCaseData(
                new Dictionary<string, HackathonEntity>
                {
                    { "a", new HackathonEntity{ CreatorId = "uid", CreatedAt = DateTime.UtcNow.AddHours(-1) } },
                    { "b", new HackathonEntity{ CreatorId = "uid", CreatedAt = DateTime.UtcNow.AddHours(-12) } },
                    { "c", new HackathonEntity{ CreatorId = "uid", CreatedAt = DateTime.UtcNow.AddHours(-23) } },
                },
                false);

            // >10 in 1 month
            Dictionary<string, HackathonEntity> month = new Dictionary<string, HackathonEntity>();
            for (int i = 0; i < 10; i++)
            {
                month.Add(i.ToString(), new HackathonEntity { CreatorId = "uid", CreatedAt = DateTime.UtcNow.AddDays(-5) });
            }
            yield return new TestCaseData(
                month,
                false);

            // pass
            Dictionary<string, HackathonEntity> pass = new Dictionary<string, HackathonEntity>();
            pass.Add("a", new HackathonEntity { CreatorId = "uid", CreatedAt = DateTime.UtcNow.AddHours(-23) });
            pass.Add("b", new HackathonEntity { CreatorId = "uid", CreatedAt = DateTime.UtcNow.AddHours(-1) });
            pass.Add("c", new HackathonEntity { CreatorId = "uid2", CreatedAt = DateTime.UtcNow.AddHours(-1) });
            for (int i = 0; i < 7; i++)
            {
                pass.Add(i.ToString(), new HackathonEntity { CreatorId = "uid", CreatedAt = DateTime.UtcNow.AddDays(-5) });
            }
            yield return new TestCaseData(
                pass,
                true);
        }

        [Test, TestCaseSource(nameof(CanCreateHackathonAsyncTestData))]
        public async Task CanCreateHackathonAsync(Dictionary<string, HackathonEntity> entities, bool expectedResult)
        {
            var user = new ClaimsPrincipal(
                    new ClaimsIdentity(new List<Claim>
                    {
                        new Claim(AuthConstant.ClaimType.UserId, "uid")
                    })
                );

            var logger = new Mock<ILogger<HackathonManagement>>();
            var cache = new Mock<ICacheProvider>();
            cache.Setup(c => c.GetOrAddAsync(It.IsAny<CacheEntry<Dictionary<string, HackathonEntity>>>(), default)).ReturnsAsync(entities);

            var hackathonManagement = new HackathonManagement(logger.Object)
            {
                Cache = cache.Object,
            };
            var result = await hackathonManagement.CanCreateHackathonAsync(user, default);

            Mock.VerifyAll(cache);
            cache.VerifyNoOtherCalls();
            Assert.AreEqual(expectedResult, result);
        }
        #endregion

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
                banners = new PictureInfo[] { new PictureInfo { name = "pn", description = "pd", uri = "pu" } },
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
            Assert.IsFalse(result.ReadOnly);

            Assert.AreEqual("loc", hackInserted.Location);
            Assert.AreEqual("uid", hackInserted.CreatorId);
            Assert.AreEqual(new string[] { "a", "b", "c" }, hackInserted.Tags);
            Assert.AreEqual(1, hackInserted.Banners.Length);
            Assert.AreEqual("pn", hackInserted.Banners[0].name);
            Assert.AreEqual("pd", hackInserted.Banners[0].description);
            Assert.AreEqual("pu", hackInserted.Banners[0].uri);
            Assert.IsFalse(hackInserted.ReadOnly);

            Assert.AreEqual("test", adminCaptured.hackathonName);
            Assert.AreEqual("uid", adminCaptured.userId);
        }
        #endregion

        #region UpdateHackathonStatusAsync
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
        #endregion

        #region UpdateHackathonReadOnlyAsync
        [TestCase(true)]
        [TestCase(false)]
        public async Task UpdateHackathonReadOnlyAsync(bool readOnly)
        {
            HackathonEntity entity = new HackathonEntity();

            var hackathonTable = new Mock<IHackathonTable>();
            hackathonTable.Setup(p => p.MergeAsync(It.Is<HackathonEntity>(h => h.ReadOnly == readOnly), default));
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.HackathonTable).Returns(hackathonTable.Object);

            var hackathonManager = new HackathonManagement(null)
            {
                StorageContext = storageContext.Object,
            };
            var result = await hackathonManager.UpdateHackathonReadOnlyAsync(entity, readOnly, default);

            Mock.VerifyAll(storageContext, hackathonTable);
            hackathonTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();

            Assert.AreEqual(readOnly, result.ReadOnly);
        }
        #endregion

        #region GetHackathonEntityByNameAsync
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
        #endregion

        #region ListPaginatedHackathonsAsync

        #region online, paging, ordering
        private static IEnumerable ListPaginatedHackathonsAsyncTestData_online()
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
                Enrollment = 2,
            };
            var h2 = new HackathonEntity
            {
                Status = HackathonStatus.online,
                PartitionKey = "h2",
                DisplayName = "asearch DisplayName",
                CreatedAt = DateTime.Now.AddDays(2),
                Timestamp = DateTimeOffset.Now.AddDays(-1),
                Enrollment = 5,
            };
            var h3 = new HackathonEntity
            {
                Status = HackathonStatus.online,
                PartitionKey = "h3",
                Detail = "search Detail",
                CreatedAt = DateTime.Now.AddDays(3),
                Timestamp = DateTimeOffset.Now.AddDays(2),
                Enrollment = 1,
            };
            var h4 = new HackathonEntity
            {
                Status = HackathonStatus.online,
                PartitionKey = "searc h4",
                CreatedAt = DateTime.Now.AddDays(4),
                Timestamp = DateTimeOffset.Now.AddDays(-2),
                Enrollment = 4,
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

            // ordering by hot
            yield return new TestCaseData(
                new Dictionary<string, HackathonEntity>
                {
                    { "offline", offline },
                    { "h1", h1 },
                    { "h2", h2 },
                    { "h3", h3 },
                    { "h4", h4 }
                },
                new HackathonQueryOptions { OrderBy = HackathonOrderBy.hot },
                new List<HackathonEntity>
                {
                    h2, h4, h1, h3
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
                    NextRowKey = "3"
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
                    NextRowKey = "3"
                }
                );
        }

        [Test, TestCaseSource(nameof(ListPaginatedHackathonsAsyncTestData_online))]
        public async Task ListPaginatedHackathonsAsync_Online(
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
            var result = await hackathonManagement.ListPaginatedHackathonsAsync(null, options, cancellationToken);

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

        #region admin
        private static IEnumerable ListPaginatedHackathonsAsyncTestData_admin()
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
            var h5 = new HackathonEntity
            {
                PartitionKey = "h5",
                CreatedAt = DateTime.Now.AddDays(4),
                Status = HackathonStatus.offline,
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
                        new Claim(AuthConstant.ClaimType.PlatformAdministrator, "foo"),
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
                    { "h4", h4 },
                    { "h5", h5 }
                },
                new Dictionary<string, List<HackathonAdminEntity>>
                {
                    { "h1", new List<HackathonAdminEntity> { } },
                    { "h2", new List<HackathonAdminEntity> { a0 } },
                    { "h3", new List<HackathonAdminEntity> { a1, a2 } },
                    { "h4", new List<HackathonAdminEntity> { a0, a1 } },
                },
                new List<HackathonEntity>
                {
                    h4, h2
                }
                );
        }

        [Test, TestCaseSource(nameof(ListPaginatedHackathonsAsyncTestData_admin))]
        public async Task ListPaginatedHackathonsAsync_admin(
            ClaimsPrincipal user,
            Dictionary<string, HackathonEntity> allHackathons,
            Dictionary<string, List<HackathonAdminEntity>> admins,
            List<HackathonEntity> expectedResult)
        {
            CancellationToken cancellationToken = CancellationToken.None;
            var options = new HackathonQueryOptions
            {
                OrderBy = HackathonOrderBy.createdAt,
                ListType = HackathonListType.admin,
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
            var result = await hackathonManagement.ListPaginatedHackathonsAsync(user, options, cancellationToken);

            Mock.VerifyAll(cache, hackathonAdminManagement);
            cache.VerifyNoOtherCalls();
            hackathonAdminManagement.VerifyNoOtherCalls();

            Assert.AreEqual(expectedResult.Count(), result.Count());
            for (int i = 0; i < result.Count(); i++)
            {
                Assert.AreEqual(expectedResult[i].Name, result.ElementAt(i).Name);
                Assert.AreEqual(expectedResult[i].CreatedAt, result.ElementAt(i).CreatedAt);
            }
        }
        #endregion

        #region enrolled
        private static IEnumerable ListPaginatedHackathonsAsyncTestData_enrolled()
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
            var h5 = new HackathonEntity
            {
                PartitionKey = "h5",
                CreatedAt = DateTime.Now.AddDays(4),
                Status = HackathonStatus.offline,
            };

            // arg0: user
            // arg1: all hackathons
            // arg2: enrolled
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

            // no userId
            yield return new TestCaseData(
                new ClaimsPrincipal(
                    new ClaimsIdentity(new List<Claim>
                    {
                        new Claim(AuthConstant.ClaimType.PlatformAdministrator, "foo"),
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
                new List<HackathonEntity>()
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
                    { "h4", h4 },
                    { "h5", h5 }
                },
                new Dictionary<string, bool>
                {
                    { "h1", true },
                    { "h2", false },
                    { "h3", true },
                    { "h4", false },
                },
                new List<HackathonEntity>
                {
                    h3, h1
                });
        }

        [Test, TestCaseSource(nameof(ListPaginatedHackathonsAsyncTestData_enrolled))]
        public async Task ListPaginatedHackathonsAsync_enrolled(
            ClaimsPrincipal user,
            Dictionary<string, HackathonEntity> allHackathons,
            Dictionary<string, bool> enrolled,
            List<HackathonEntity> expectedResult)
        {
            CancellationToken cancellationToken = CancellationToken.None;
            var options = new HackathonQueryOptions
            {
                OrderBy = HackathonOrderBy.createdAt,
                ListType = HackathonListType.enrolled,
            };

            var logger = new Mock<ILogger<HackathonManagement>>();
            var cache = new Mock<ICacheProvider>();
            var enrollmentManagement = new Mock<IEnrollmentManagement>();

            string userId = ClaimsHelper.GetUserId(user);
            if (!string.IsNullOrWhiteSpace(userId))
            {
                cache.Setup(c => c.GetOrAddAsync(It.IsAny<CacheEntry<Dictionary<string, HackathonEntity>>>(), cancellationToken))
                    .ReturnsAsync(allHackathons);

                foreach (var h in allHackathons.Values)
                {
                    if (enrolled.ContainsKey(h.Name))
                    {
                        enrollmentManagement.Setup(e => e.IsUserEnrolledAsync(h, userId, cancellationToken)).ReturnsAsync(enrolled[h.Name]);
                    }
                }
            }

            var hackathonManagement = new HackathonManagement(logger.Object)
            {
                Cache = cache.Object,
                EnrollmentManagement = enrollmentManagement.Object,
            };
            var result = await hackathonManagement.ListPaginatedHackathonsAsync(user, options, cancellationToken);

            Mock.VerifyAll(cache, enrollmentManagement);
            cache.VerifyNoOtherCalls();
            enrollmentManagement.VerifyNoOtherCalls();

            Assert.AreEqual(expectedResult.Count(), result.Count());
            for (int i = 0; i < result.Count(); i++)
            {
                Assert.AreEqual(expectedResult[i].Name, result.ElementAt(i).Name);
                Assert.AreEqual(expectedResult[i].CreatedAt, result.ElementAt(i).CreatedAt);
            }
        }
        #endregion

        #region fresh
        private static IEnumerable ListPaginatedHackathonsAsyncTestData_fresh()
        {
            //  EventStartedAt = null
            var h1 = new HackathonEntity
            {
                PartitionKey = "h1",
                CreatedAt = DateTime.Now.AddDays(1),
            };
            // status != online
            var h2 = new HackathonEntity
            {
                PartitionKey = "h2",
                CreatedAt = DateTime.Now.AddDays(2),
                EventStartedAt = DateTime.Now.AddDays(2),
            };
            // already started
            var h3 = new HackathonEntity
            {
                PartitionKey = "h3",
                CreatedAt = DateTime.Now.AddDays(3),
                Status = HackathonStatus.online,
                EventStartedAt = DateTime.Now.AddDays(-3),
            };
            // qualified
            var h4 = new HackathonEntity
            {
                PartitionKey = "h4",
                CreatedAt = DateTime.Now.AddDays(4),
                Status = HackathonStatus.online,
                EventStartedAt = DateTime.Now.AddDays(1),
            };

            // arg0: user
            // arg1: all hackathons
            // arg2: enrolled
            // arg3: expected result

            // normal user
            yield return new TestCaseData(
                new Dictionary<string, HackathonEntity>
                {
                    { "h1", h1 },
                    { "h2", h2 },
                    { "h3", h3 },
                    { "h4", h4 }
                },
                new List<HackathonEntity>
                {
                    h4
                });
        }

        [Test, TestCaseSource(nameof(ListPaginatedHackathonsAsyncTestData_fresh))]
        public async Task ListPaginatedHackathonsAsync_fresh(
            Dictionary<string, HackathonEntity> allHackathons,
            List<HackathonEntity> expectedResult)
        {
            CancellationToken cancellationToken = CancellationToken.None;
            var options = new HackathonQueryOptions
            {
                OrderBy = HackathonOrderBy.createdAt,
                ListType = HackathonListType.fresh,
            };

            var logger = new Mock<ILogger<HackathonManagement>>();
            var cache = new Mock<ICacheProvider>();
            cache.Setup(c => c.GetOrAddAsync(It.IsAny<CacheEntry<Dictionary<string, HackathonEntity>>>(), cancellationToken))
                .ReturnsAsync(allHackathons);

            var hackathonManagement = new HackathonManagement(logger.Object)
            {
                Cache = cache.Object,
            };
            var result = await hackathonManagement.ListPaginatedHackathonsAsync(null, options, cancellationToken);

            Mock.VerifyAll(cache);
            cache.VerifyNoOtherCalls();

            Assert.AreEqual(expectedResult.Count(), result.Count());
            for (int i = 0; i < result.Count(); i++)
            {
                Assert.AreEqual(expectedResult[i].Name, result.ElementAt(i).Name);
                Assert.AreEqual(expectedResult[i].CreatedAt, result.ElementAt(i).CreatedAt);
            }
        }
        #endregion

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

        #region UpdateHackathonAsyncTest
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
        #endregion

        #region ListHackathonRolesAsync
        [Test]
        public async Task ListHackathonRolesAsync()
        {
            var hackathons = new List<HackathonEntity>
            {
                new HackathonEntity{ PartitionKey = "hack1", },
                new HackathonEntity{ PartitionKey = "hack2", },
            };
            var user = new ClaimsPrincipal(new ClaimsIdentity(new List<Claim>
            {
                new Claim(AuthConstant.ClaimType.UserId, "uid")
            }));
            var admins1 = new List<HackathonAdminEntity>
            {
                new HackathonAdminEntity{ RowKey = "other" }
            };
            var admins2 = new List<HackathonAdminEntity>
            {
                new HackathonAdminEntity{ RowKey = "uid" }
            };

            var hackathonAdminManagement = new Mock<IHackathonAdminManagement>();
            hackathonAdminManagement.Setup(a => a.ListHackathonAdminAsync("hack1", default))
                .ReturnsAsync(admins1);
            hackathonAdminManagement.Setup(a => a.ListHackathonAdminAsync("hack2", default))
               .ReturnsAsync(admins2);

            var enrollmentManagement = new Mock<IEnrollmentManagement>();
            enrollmentManagement.Setup(e => e.IsUserEnrolledAsync(hackathons.ElementAt(0), "uid", default)).ReturnsAsync(false);
            enrollmentManagement.Setup(e => e.IsUserEnrolledAsync(hackathons.ElementAt(1), "uid", default)).ReturnsAsync(true);

            var judgeManagement = new Mock<IJudgeManagement>();
            judgeManagement.Setup(j => j.IsJudgeAsync("hack1", "uid", default)).ReturnsAsync(false);
            judgeManagement.Setup(j => j.IsJudgeAsync("hack2", "uid", default)).ReturnsAsync(true);

            var hackathonManagement = new HackathonManagement(null)
            {
                HackathonAdminManagement = hackathonAdminManagement.Object,
                EnrollmentManagement = enrollmentManagement.Object,
                JudgeManagement = judgeManagement.Object,
            };

            var result = await hackathonManagement.ListHackathonRolesAsync(hackathons, user, default);

            Mock.VerifyAll(hackathonAdminManagement, enrollmentManagement);
            hackathonAdminManagement.VerifyNoOtherCalls();
            enrollmentManagement.VerifyNoOtherCalls();

            Assert.IsFalse(result.ElementAt(0).Item2.isAdmin);
            Assert.IsFalse(result.ElementAt(0).Item2.isEnrolled);
            Assert.IsFalse(result.ElementAt(0).Item2.isJudge);

            Assert.IsTrue(result.ElementAt(1).Item2.isAdmin);
            Assert.IsTrue(result.ElementAt(1).Item2.isEnrolled);
            Assert.IsTrue(result.ElementAt(1).Item2.isJudge);
        }
        #endregion

        #region GetHackathonRolesAsync
        [Test]
        public async Task GetHackathonRolesAsyncTest_NoUserIdClaim()
        {
            HackathonEntity hackathon = new HackathonEntity { PartitionKey = "hack" };
            ClaimsPrincipal user = new ClaimsPrincipal();
            ClaimsPrincipal user2 = new ClaimsPrincipal(new ClaimsIdentity(new List<Claim>
            {
                new Claim(AuthConstant.ClaimType.PlatformAdministrator, "uid"),
            }));
            CancellationToken cancellationToken = CancellationToken.None;

            var hackathonManagement = new HackathonManagement(null);
            Assert.IsNull(await hackathonManagement.GetHackathonRolesAsync(hackathon, null, cancellationToken));
            Assert.IsNull(await hackathonManagement.GetHackathonRolesAsync(hackathon, user, cancellationToken));
            Assert.IsNull(await hackathonManagement.GetHackathonRolesAsync(hackathon, user2, cancellationToken));
            Assert.IsNull(await hackathonManagement.GetHackathonRolesAsync(null, user, cancellationToken));
        }

        private static IEnumerable GetHackathonRolesAsyncTestData()
        {
            // arg0: user
            // arg1: admins
            // arg2: enrolled
            // arg3: isJudge
            // expected roles

            // platform admin
            yield return new TestCaseData(
                new ClaimsPrincipal(new ClaimsIdentity(new List<Claim>
                {
                    new Claim(AuthConstant.ClaimType.UserId, "uid"),
                    new Claim(AuthConstant.ClaimType.PlatformAdministrator, "uid"),
                })),
                null,
                false,
                false,
                new HackathonRoles
                {
                    isAdmin = true,
                    isEnrolled = false,
                    isJudge = false
                });

            // hack admin
            yield return new TestCaseData(
                new ClaimsPrincipal(new ClaimsIdentity(new List<Claim>
                {
                    new Claim(AuthConstant.ClaimType.UserId, "uid"),
                })),
                new List<HackathonAdminEntity>
                {
                    new HackathonAdminEntity { PartitionKey="hack", RowKey="uid" },
                },
                false,
                false,
                new HackathonRoles
                {
                    isAdmin = true,
                    isEnrolled = false,
                    isJudge = false
                });

            // neither platform nor hack admin
            yield return new TestCaseData(
                new ClaimsPrincipal(new ClaimsIdentity(new List<Claim>
                {
                    new Claim(AuthConstant.ClaimType.UserId, "uid"),
                })),
                new List<HackathonAdminEntity>
                {
                    new HackathonAdminEntity { PartitionKey="hack", RowKey="other" },
                    new HackathonAdminEntity { PartitionKey="hack", RowKey="other2" }
                },
                false,
                false,
                new HackathonRoles
                {
                    isAdmin = false,
                    isEnrolled = false,
                    isJudge = false
                });

            // enrolled
            yield return new TestCaseData(
                new ClaimsPrincipal(new ClaimsIdentity(new List<Claim>
                {
                    new Claim(AuthConstant.ClaimType.UserId, "uid"),
                    new Claim(AuthConstant.ClaimType.PlatformAdministrator, "uid"),
                })),
                null,
                true,
                false,
                new HackathonRoles
                {
                    isAdmin = true,
                    isEnrolled = true,
                    isJudge = false
                });

            // judge
            yield return new TestCaseData(
                new ClaimsPrincipal(new ClaimsIdentity(new List<Claim>
                {
                    new Claim(AuthConstant.ClaimType.UserId, "uid"),
                    new Claim(AuthConstant.ClaimType.PlatformAdministrator, "uid"),
                })),
                null,
                false,
                true,
                new HackathonRoles
                {
                    isAdmin = true,
                    isEnrolled = false,
                    isJudge = true
                });
        }

        [Test, TestCaseSource(nameof(GetHackathonRolesAsyncTestData))]
        public async Task GetHackathonRolesAsync(ClaimsPrincipal user, IEnumerable<HackathonAdminEntity> admins, bool enrolled, bool isJudge, HackathonRoles expectedRoles)
        {
            HackathonEntity hackathon = new HackathonEntity { PartitionKey = "hack" };

            var hackathonAdminManagement = new Mock<IHackathonAdminManagement>();
            if (admins != null)
            {
                hackathonAdminManagement.Setup(h => h.ListHackathonAdminAsync(hackathon.Name, default)).ReturnsAsync(admins);
            }
            var enrollmentManagement = new Mock<IEnrollmentManagement>();
            enrollmentManagement.Setup(h => h.IsUserEnrolledAsync(hackathon, "uid", default)).ReturnsAsync(enrolled);
            var judgeManagement = new Mock<IJudgeManagement>();
            judgeManagement.Setup(j => j.IsJudgeAsync("hack", "uid", default)).ReturnsAsync(isJudge);

            var hackathonManagement = new HackathonManagement(null)
            {
                EnrollmentManagement = enrollmentManagement.Object,
                HackathonAdminManagement = hackathonAdminManagement.Object,
                JudgeManagement = judgeManagement.Object,
            };
            var role = await hackathonManagement.GetHackathonRolesAsync(hackathon, user, default);


            Mock.VerifyAll(enrollmentManagement, hackathonAdminManagement, judgeManagement);
            enrollmentManagement.VerifyNoOtherCalls();
            hackathonAdminManagement.VerifyNoOtherCalls();
            judgeManagement.VerifyNoOtherCalls();

            Assert.AreEqual(expectedRoles.isAdmin, role.isAdmin);
            Assert.AreEqual(expectedRoles.isEnrolled, role.isEnrolled);
            Assert.AreEqual(expectedRoles.isJudge, role.isJudge);
        }
        #endregion
    }
}
