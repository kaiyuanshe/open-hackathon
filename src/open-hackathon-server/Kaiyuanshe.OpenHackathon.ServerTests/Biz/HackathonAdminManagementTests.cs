using Kaiyuanshe.OpenHackathon.Server.Auth;
using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Cache;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Storage;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Kaiyuanshe.OpenHackathon.Server.Storage.Tables;
using Microsoft.Extensions.Logging;
using Moq;
using NUnit.Framework;
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
            var cancellationToken = CancellationToken.None;

            var logger = new Mock<ILogger<HackathonAdminManagement>>();
            var hackathonAdminTable = new Mock<IHackathonAdminTable>();
            HackathonAdminEntity captured = null;
            hackathonAdminTable.Setup(a => a.InsertAsync(It.IsAny<HackathonAdminEntity>(), cancellationToken))
                .Callback<HackathonAdminEntity, CancellationToken>((en, ct) =>
                {
                    captured = en;
                });
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.HackathonAdminTable).Returns(hackathonAdminTable.Object);
            var cache = new Mock<ICacheProvider>();
            cache.Setup(c => c.Remove("HackathonAdmin-hack"));

            var management = new HackathonAdminManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
                Cache = cache.Object,
            };
            var result = await management.CreateAdminAsync(admin, cancellationToken);

            Mock.VerifyAll(hackathonAdminTable, storageContext, cache);
            hackathonAdminTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            cache.VerifyNoOtherCalls();
            Assert.AreEqual("hack", captured.HackathonName);
            Assert.AreEqual("uid", captured.UserId);
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
