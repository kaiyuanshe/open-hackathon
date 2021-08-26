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
    public class HackathonAdminManagementTests
    {
        #region CreateAdminAsync
        [Test]
        public async Task CreateAdminAsync()
        {
            var admin = new HackathonAdmin
            {
                hackathonName = "hack",
                userId = "uid"
            };

            var logger = new Mock<ILogger<HackathonAdminManagement>>();
            var hackathonAdminTable = new Mock<IHackathonAdminTable>();
            hackathonAdminTable.Setup(a => a.InsertOrMergeAsync(It.Is<HackathonAdminEntity>(a =>
                    a.HackathonName == "hack" && a.UserId == "uid"),
                    default));

            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.HackathonAdminTable).Returns(hackathonAdminTable.Object);

            var cache = new Mock<ICacheProvider>();
            cache.Setup(c => c.Remove("HackathonAdmin-hack"));

            var management = new HackathonAdminManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
                Cache = cache.Object,
            };
            var result = await management.CreateAdminAsync(admin, default);

            Mock.VerifyAll(hackathonAdminTable, storageContext, cache);
            hackathonAdminTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            cache.VerifyNoOtherCalls();

            Assert.AreEqual("hack", result.HackathonName);
            Assert.AreEqual("uid", result.UserId);
        }
        #endregion

        #region ListHackathonAdminAsyncTest
        [Test]
        public async Task ListHackathonAdminAsyncTest()
        {
            string name = "hack";
            CancellationToken cancellationToken = CancellationToken.None;
            var data = new List<HackathonAdminEntity>()
            {
                new HackathonAdminEntity{ PartitionKey="pk1", },
                new HackathonAdminEntity{ PartitionKey="pk2", },
            };

            var storageContext = new Mock<IStorageContext>();
            var hackAdminTable = new Mock<IHackathonAdminTable>();
            storageContext.SetupGet(p => p.HackathonAdminTable).Returns(hackAdminTable.Object);
            hackAdminTable.Setup(p => p.ListByHackathonAsync(name, cancellationToken)).ReturnsAsync(data);
            var cache = new DefaultCacheProvider(null);

            var hackathonAdminManagement = new HackathonAdminManagement(null)
            {
                StorageContext = storageContext.Object,
                Cache = cache,
            };
            var results = await hackathonAdminManagement.ListHackathonAdminAsync(name, cancellationToken);

            Mock.VerifyAll(storageContext, hackAdminTable);
            hackAdminTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            Assert.AreEqual(2, results.Count());
            Assert.AreEqual("pk1", results.First().HackathonName);
            Assert.AreEqual("pk2", results.Last().HackathonName);
        }
        #endregion

        #region ListPaginatedHackathonAdminAsync
        private static IEnumerable ListPaginatedHackathonAdminAsyncTestData()
        {
            var a1 = new HackathonAdminEntity
            {
                RowKey = "a1",
                CreatedAt = DateTime.UtcNow.AddDays(1),
            };
            var a2 = new HackathonAdminEntity
            {
                RowKey = "a1",
                CreatedAt = DateTime.UtcNow.AddDays(3),
            };
            var a3 = new HackathonAdminEntity
            {
                RowKey = "a1",
                CreatedAt = DateTime.UtcNow.AddDays(2),
            };
            var a4 = new HackathonAdminEntity
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
                new AdminQueryOptions { },
                new List<HackathonAdminEntity> { a1, a2, a3, a4 },
                new List<HackathonAdminEntity> { a4, a2, a3, a1 },
                null
                );

            // by Team
            yield return new TestCaseData(
                new AdminQueryOptions { },
                new List<HackathonAdminEntity> { a1, a2, a3, a4 },
                new List<HackathonAdminEntity> { a4, a2, a3, a1 },
                null
                );

            // by Hackathon
            yield return new TestCaseData(
                new AdminQueryOptions { },
                new List<HackathonAdminEntity> { a1, a2, a3, a4 },
                new List<HackathonAdminEntity> { a4, a2, a3, a1 },
                null
                );

            // top
            yield return new TestCaseData(
                new AdminQueryOptions { Top = 2, },
                new List<HackathonAdminEntity> { a1, a2, a3, a4 },
                new List<HackathonAdminEntity> { a4, a2, },
                new TableContinuationToken { NextPartitionKey = "2", NextRowKey = "2" }
                );

            // paging
            yield return new TestCaseData(
                new AdminQueryOptions
                {
                    Top = 2,
                    TableContinuationToken = new TableContinuationToken
                    {
                        NextPartitionKey = "1",
                        NextRowKey = "1"
                    },
                },
                new List<HackathonAdminEntity> { a1, a2, a3, a4 },
                new List<HackathonAdminEntity> { a2, a3, },
                new TableContinuationToken { NextPartitionKey = "3", NextRowKey = "3" }
                );
        }

        [Test, TestCaseSource(nameof(ListPaginatedHackathonAdminAsyncTestData))]
        public async Task ListPaginatedHackathonAdminAsync(
            AdminQueryOptions options,
            IEnumerable<HackathonAdminEntity> all,
            IEnumerable<HackathonAdminEntity> expectedResult,
            TableContinuationToken expectedNext)
        {
            string hackName = "hack";

            var logger = new Mock<ILogger<HackathonAdminManagement>>();
            var cache = new Mock<ICacheProvider>();
            cache.Setup(c => c.GetOrAddAsync(It.Is<CacheEntry<IEnumerable<HackathonAdminEntity>>>(c => c.CacheKey == "HackathonAdmin-hack"), default)).ReturnsAsync(all);

            var adminManagement = new HackathonAdminManagement(logger.Object)
            {
                Cache = cache.Object,
            };
            var result = await adminManagement.ListPaginatedHackathonAdminAsync(hackName, options, default);

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

        #region GetAdminAsync
        [Test]
        public async Task GetAdminAsync()
        {
            var adminEntity = new HackathonAdminEntity { PartitionKey = "pk" };

            var logger = new Mock<ILogger<HackathonAdminManagement>>();
            var hackathonAdminTable = new Mock<IHackathonAdminTable>();
            hackathonAdminTable.Setup(a => a.RetrieveAsync("hack", "uid", default)).ReturnsAsync(adminEntity);

            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.HackathonAdminTable).Returns(hackathonAdminTable.Object);

            var management = new HackathonAdminManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
            };
            var result = await management.GetAdminAsync("hack", "uid", default);

            Mock.VerifyAll(storageContext, hackathonAdminTable);
            storageContext.VerifyNoOtherCalls();
            hackathonAdminTable.VerifyNoOtherCalls();

            Assert.AreEqual("pk", result.HackathonName);
        }
        #endregion

        #region DeleteAdminAsync
        [Test]
        public async Task DeleteAdminAsync()
        {
            var logger = new Mock<ILogger<HackathonAdminManagement>>();
            var hackathonAdminTable = new Mock<IHackathonAdminTable>();
            hackathonAdminTable.Setup(a => a.DeleteAsync("hack", "uid", default));

            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.HackathonAdminTable).Returns(hackathonAdminTable.Object);

            var management = new HackathonAdminManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
            };
            await management.DeleteAdminAsync("hack", "uid", default);

            Mock.VerifyAll(storageContext, hackathonAdminTable);
            storageContext.VerifyNoOtherCalls();
            hackathonAdminTable.VerifyNoOtherCalls();

        }
        #endregion

        #region IsHackathonAdmin
        private static IEnumerable IsHackathonAdminTestData()
        {
            // arg0: user
            // arg1: admins
            // arg2: expected result

            // no userId
            yield return new TestCaseData(
                new ClaimsPrincipal(new ClaimsIdentity(new List<Claim>
                {
                })),
                null,
                false);

            // platform admin
            yield return new TestCaseData(
                new ClaimsPrincipal(new ClaimsIdentity(new List<Claim>
                {
                    new Claim(AuthConstant.ClaimType.UserId, "uid"),
                    new Claim(AuthConstant.ClaimType.PlatformAdministrator, "uid"),
                })),
                null,
                true);

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
                true);

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
                false);
        }

        [Test, TestCaseSource(nameof(IsHackathonAdminTestData))]
        public async Task IsHackathonAdmin(ClaimsPrincipal user, IEnumerable<HackathonAdminEntity> admins, bool expectedResult)
        {
            var cache = new Mock<ICacheProvider>();
            if (admins != null)
            {
                cache.Setup(h => h.GetOrAddAsync(It.IsAny<CacheEntry<IEnumerable<HackathonAdminEntity>>>(), default)).ReturnsAsync(admins);
            }

            var hackathonAdminManagement = new Mock<HackathonAdminManagement>(null) { CallBase = true };
            hackathonAdminManagement.Object.Cache = cache.Object;

            var result = await hackathonAdminManagement.Object.IsHackathonAdmin("hack", user, default);

            Mock.VerifyAll(hackathonAdminManagement, cache);
            hackathonAdminManagement.VerifyNoOtherCalls();
            cache.VerifyNoOtherCalls();

            Assert.AreEqual(expectedResult, result);
        }

        #endregion
    }
}
