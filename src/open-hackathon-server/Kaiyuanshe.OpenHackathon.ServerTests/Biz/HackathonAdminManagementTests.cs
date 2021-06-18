using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Storage;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Kaiyuanshe.OpenHackathon.Server.Storage.Tables;
using Microsoft.Extensions.Logging;
using Moq;
using NUnit.Framework;
using System;
using System.Collections.Generic;
using System.Text;
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

            var management = new HackathonAdminManagement(logger.Object)
            {
                StorageContext = storageContext.Object
            };
            var result = await management.CreateAdminAsync(admin, cancellationToken);

            Mock.VerifyAll(hackathonAdminTable, storageContext);
            hackathonAdminTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            Assert.AreEqual("hack", captured.HackathonName);
            Assert.AreEqual("uid", captured.UserId);
            Assert.AreEqual("hack", result.HackathonName);
            Assert.AreEqual("uid", result.UserId);
        }
        #endregion
    }
}
