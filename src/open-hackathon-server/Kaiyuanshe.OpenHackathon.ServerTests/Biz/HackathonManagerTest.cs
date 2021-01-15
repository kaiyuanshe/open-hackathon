using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Storage;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Kaiyuanshe.OpenHackathon.Server.Storage.Tables;
using Microsoft.WindowsAzure.Storage.Table;
using Moq;
using NUnit.Framework;
using System;
using System.Collections.Generic;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Biz
{
    [TestFixture]
    public class HackathonManagerTest
    {
        [Test]
        public async Task GetHackathonEntityByNameAsyncTest()
        {
            string name = "test";
            var entity = new HackathonEntity
            {
                Location = "loc"
            };

            var hackathonTableMock = new Mock<IHackathonTable>();
            hackathonTableMock.Setup(p => p.RetrieveAsync(name, string.Empty, CancellationToken.None))
                .ReturnsAsync(entity);

            var storageContextMock = new Mock<IStorageContext>();
            storageContextMock.SetupGet(p => p.HackathonTable).Returns(hackathonTableMock.Object);

            var hackathonManager = new HackathonManager();
            hackathonManager.StorageContext = storageContextMock.Object;
            var result = await hackathonManager.GetHackathonEntityByNameAsync(name, CancellationToken.None);

            Mock.VerifyAll();
            hackathonTableMock.Verify(p => p.RetrieveAsync(name, string.Empty, CancellationToken.None), Times.Once);
            hackathonTableMock.VerifyNoOtherCalls();

            storageContextMock.VerifyGet(p => p.HackathonTable, Times.Once);
            storageContextMock.VerifyNoOtherCalls();

            Assert.AreEqual("loc", result.Location);
        }

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
                Name = name,
            };

            var hackathonTableMock = new Mock<IHackathonTable>();
            hackathonTableMock.Setup(p => p.RetrieveAndMergeAsync(name, string.Empty, It.IsAny<Action<HackathonEntity>>(), CancellationToken.None))
                .ReturnsAsync(default(TableResult));
            hackathonTableMock.Setup(p => p.RetrieveAsync(name, string.Empty, CancellationToken.None))
                .ReturnsAsync(entity);

            var storageContextMock = new Mock<IStorageContext>();
            storageContextMock.SetupGet(p => p.HackathonTable).Returns(hackathonTableMock.Object);

            var hackathonManager = new HackathonManager();
            hackathonManager.StorageContext = storageContextMock.Object;
            var result = await hackathonManager.UpdateHackathonAsync(request, CancellationToken.None);

            Mock.VerifyAll();
            hackathonTableMock.Verify(p => p.RetrieveAndMergeAsync(name, string.Empty, It.IsAny<Action<HackathonEntity>>(), CancellationToken.None), Times.Once);
            hackathonTableMock.Verify(p => p.RetrieveAsync(name, string.Empty, CancellationToken.None), Times.Once);
            hackathonTableMock.VerifyNoOtherCalls();

            storageContextMock.VerifyGet(p => p.HackathonTable, Times.Exactly(2));
            storageContextMock.VerifyNoOtherCalls();

            Assert.AreEqual("loc", result.Location);
        }

        [Test]
        public async Task CreateHackathonAsyncTest()
        {
            var request = new Hackathon
            {
                Name = "test",
                Location = "loc",
                EventStartTime = DateTime.UtcNow,
            };

            var hackathonTableMock = new Mock<IHackathonTable>();
            hackathonTableMock.Setup(p => p.InsertAsync(It.IsAny<HackathonEntity>(), CancellationToken.None));

            var storageContextMock = new Mock<IStorageContext>();
            storageContextMock.SetupGet(p => p.HackathonTable).Returns(hackathonTableMock.Object);

            var hackathonManager = new HackathonManager();
            hackathonManager.StorageContext = storageContextMock.Object;
            var result = await hackathonManager.CreateHackathonAsync(request, CancellationToken.None);

            Mock.VerifyAll();
            hackathonTableMock.Verify(p => p.InsertAsync(It.IsAny<HackathonEntity>(), CancellationToken.None), Times.Once);
            hackathonTableMock.VerifyNoOtherCalls();

            storageContextMock.VerifyGet(p => p.HackathonTable, Times.Once);
            storageContextMock.VerifyNoOtherCalls();

            Assert.AreEqual("loc", result.Location);
            Assert.AreEqual("test", result.PartitionKey);
            Assert.AreEqual(string.Empty, result.RowKey);
            Assert.IsTrue(result.EventStartTime.HasValue);
            Assert.IsFalse(result.EventEndTime.HasValue);
        }
    }
}
