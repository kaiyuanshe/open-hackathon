using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Storage;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Kaiyuanshe.OpenHackathon.Server.Storage.Tables;
using Microsoft.Extensions.Logging;
using Microsoft.WindowsAzure.Storage.Table;
using Moq;
using NUnit.Framework;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Biz
{
    [TestFixture]
    public class HackathonManagementTest
    {
        [Test]
        public async Task CreateHackathonAsyncTest()
        {
            // input
            var request = new Hackathon
            {
                name = "test",
                location = "loc",
                eventStartedAt = DateTime.UtcNow,
            };
            CancellationToken cancellationToken = CancellationToken.None;

            // capture
            HackathonEntity hackInserted = null;
            ParticipantEntity partInserted = null;

            // mock
            var hackathonTableMock = new Mock<IHackathonTable>();
            hackathonTableMock.Setup(p => p.InsertAsync(It.IsAny<HackathonEntity>(), cancellationToken))
                .Callback<HackathonEntity, CancellationToken>((h, c) => { hackInserted = h; });

            var participantTableMock = new Mock<IParticipantTable>();
            participantTableMock.Setup(p => p.InsertAsync(It.IsAny<ParticipantEntity>(), cancellationToken))
                .Callback<ParticipantEntity, CancellationToken>((h, c) => { partInserted = h; });

            var storageContextMock = new Mock<IStorageContext>();
            storageContextMock.SetupGet(p => p.HackathonTable).Returns(hackathonTableMock.Object);
            storageContextMock.SetupGet(p => p.ParticipantTable).Returns(participantTableMock.Object);

            // test
            var hackathonManager = new HackathonManagement(null);
            hackathonManager.StorageContext = storageContextMock.Object;
            var result = await hackathonManager.CreateHackathonAsync(request, CancellationToken.None);

            // verify
            Mock.VerifyAll(hackathonTableMock, participantTableMock, storageContextMock);
            hackathonTableMock.VerifyNoOtherCalls();
            participantTableMock.VerifyNoOtherCalls();
            storageContextMock.VerifyNoOtherCalls();

            Assert.AreEqual("loc", result.Location);
            Assert.AreEqual("test", result.PartitionKey);
            Assert.AreEqual(string.Empty, result.RowKey);
            Assert.IsTrue(result.EventStartedAt.HasValue);
            Assert.IsFalse(result.EventEndedAt.HasValue);
            Assert.AreEqual("loc", hackInserted.Location);
            Assert.AreEqual("test", partInserted.PartitionKey);
            Assert.IsFalse(hackInserted.IsDeleted);
        }

        [Test]
        public async Task DeleteHackathonLogicallyTest()
        {
            string name = "foo";
            CancellationToken cancellationToken = CancellationToken.None;
            Action<HackathonEntity> capturedAction = null;

            var hackathonTable = new Mock<IHackathonTable>();
            hackathonTable.Setup(p => p.RetrieveAndMergeAsync(name, string.Empty, It.IsAny<Action<HackathonEntity>>(), cancellationToken))
                .Callback<string, string, Action<HackathonEntity>, CancellationToken>((pk, rk, action, ct) =>
                {
                    capturedAction = action;
                });
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.HackathonTable).Returns(hackathonTable.Object);

            var hackathonManagement = new HackathonManagement(null)
            {
                StorageContext = storageContext.Object
            };
            await hackathonManagement.DeleteHackathonLogically(name, cancellationToken);

            Mock.VerifyAll(storageContext, hackathonTable);
            hackathonTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            var entity = new HackathonEntity { IsDeleted = false };
            capturedAction(entity);
            Assert.IsTrue(entity.IsDeleted);
        }

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

            var hackathonManager = new HackathonManagement(null);
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
        public async Task ListHackathonAdminAsyncTest()
        {
            string name = "hack";
            CancellationToken cancellationToken = CancellationToken.None;
            var data = new List<ParticipantEntity>()
            {
                new ParticipantEntity{ PartitionKey="pk1", Role = ParticipantRole.None },
                new ParticipantEntity{ PartitionKey="pk2", Role = ParticipantRole.Administrator },
                new ParticipantEntity{ PartitionKey="pk3", Role = ParticipantRole.Administrator|ParticipantRole.Judge },
                new ParticipantEntity{ PartitionKey="pk4", Role = ParticipantRole.Contestant },
            };

            var storageContext = new Mock<IStorageContext>();
            var participantTable = new Mock<IParticipantTable>();
            storageContext.SetupGet(p => p.ParticipantTable).Returns(participantTable.Object);
            participantTable.Setup(p => p.ListParticipantsByHackathonAsync(name, cancellationToken)).ReturnsAsync(data);

            var hackathonManagement = new HackathonManagement(null)
            {
                StorageContext = storageContext.Object,
            };
            var results = await hackathonManagement.ListHackathonAdminAsync(name, cancellationToken);

            Mock.VerifyAll(storageContext, participantTable);
            participantTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            Assert.AreEqual(2, results.Count());
            Assert.AreEqual("pk2", results.First().HackathonName);
            Assert.AreEqual("pk3", results.Last().HackathonName);
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
                name = name,
            };

            var hackathonTableMock = new Mock<IHackathonTable>();
            hackathonTableMock.Setup(p => p.RetrieveAndMergeAsync(name, string.Empty, It.IsAny<Action<HackathonEntity>>(), CancellationToken.None))
                .ReturnsAsync(default(TableResult));
            hackathonTableMock.Setup(p => p.RetrieveAsync(name, string.Empty, CancellationToken.None))
                .ReturnsAsync(entity);

            var storageContextMock = new Mock<IStorageContext>();
            storageContextMock.SetupGet(p => p.HackathonTable).Returns(hackathonTableMock.Object);

            var hackathonManager = new HackathonManagement(null);
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
        public async Task EnrollAsyncTest_Enrolled()
        {
            HackathonEntity hackathon = new HackathonEntity
            {
                PartitionKey = "hack"
            };
            string userId = "uid";
            ParticipantEntity participant = new ParticipantEntity
            {
                Role = ParticipantRole.Contestant | ParticipantRole.Judge
            };
            CancellationToken cancellation = CancellationToken.None;
            var logger = new Mock<ILogger<HackathonManagement>>();

            var participantTable = new Mock<IParticipantTable>();
            participantTable.Setup(p => p.RetrieveAsync("hack", userId, cancellation)).ReturnsAsync(participant);
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.ParticipantTable).Returns(participantTable.Object);

            var hackathonManagement = new HackathonManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
            };
            await hackathonManagement.EnrollAsync(hackathon, userId, cancellation);

            Mock.VerifyAll(storageContext, participantTable);
            participantTable.VerifyNoOtherCalls();
        }

        [TestCase(false, EnrollmentStatus.Pending)]
        [TestCase(true, EnrollmentStatus.Approved)]
        public async Task EnrollAsyncTest_Merge(bool autoApprove, EnrollmentStatus targetStatus)
        {
            HackathonEntity hackathon = new HackathonEntity
            {
                PartitionKey = "hack",
                AutoApprove = autoApprove,
            };
            string userId = "uid";
            ParticipantEntity participant = new ParticipantEntity();
            CancellationToken cancellation = CancellationToken.None;
            var logger = new Mock<ILogger<HackathonManagement>>();

            var participantTable = new Mock<IParticipantTable>();
            participantTable.Setup(p => p.RetrieveAsync("hack", userId, cancellation)).ReturnsAsync(participant);
            participantTable.Setup(p => p.MergeAsync(participant, cancellation));
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.ParticipantTable).Returns(participantTable.Object);

            var hackathonManagement = new HackathonManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
            };
            await hackathonManagement.EnrollAsync(hackathon, userId, cancellation);

            Mock.VerifyAll(storageContext, participantTable);
            participantTable.VerifyNoOtherCalls();
            Assert.AreEqual(targetStatus, participant.Status);
            Assert.IsTrue(participant.Role.HasFlag(ParticipantRole.Contestant));
        }

        [TestCase(false, EnrollmentStatus.Pending)]
        [TestCase(true, EnrollmentStatus.Approved)]
        public async Task EnrollAsyncTest_Insert(bool autoApprove, EnrollmentStatus targetStatus)
        {
            HackathonEntity hackathon = new HackathonEntity
            {
                PartitionKey = "hack",
                AutoApprove = autoApprove,
            };
            string userId = "uid";
            ParticipantEntity participant = null;
            CancellationToken cancellation = CancellationToken.None;
            var logger = new Mock<ILogger<HackathonManagement>>();

            var participantTable = new Mock<IParticipantTable>();
            participantTable.Setup(p => p.RetrieveAsync("hack", userId, cancellation)).ReturnsAsync(participant);
            participantTable.Setup(p => p.InsertAsync(It.IsAny<ParticipantEntity>(), cancellation))
                .Callback<ParticipantEntity, CancellationToken>((p, c) =>
                {
                    participant = p;
                });
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.ParticipantTable).Returns(participantTable.Object);

            var hackathonManagement = new HackathonManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
            };
            await hackathonManagement.EnrollAsync(hackathon, userId, cancellation);

            Mock.VerifyAll(storageContext, participantTable);
            participantTable.VerifyNoOtherCalls();
            Assert.AreEqual(targetStatus, participant.Status);
            Assert.IsTrue(participant.Role.HasFlag(ParticipantRole.Contestant));
        }

        [Test]
        public async Task EnrollUpdateStatusAsyncTest_Null()
        {
            ParticipantEntity participant = null;
            CancellationToken cancellation = CancellationToken.None;
            var logger = new Mock<ILogger<HackathonManagement>>();

            var hackathonManagement = new HackathonManagement(logger.Object);
            await hackathonManagement.EnrollmentUpdateStatusAsync(participant, EnrollmentStatus.Approved, cancellation);

            Mock.VerifyAll(logger);
            logger.VerifyNoOtherCalls();
            Assert.IsNull(participant);
        }

        [TestCase(EnrollmentStatus.Approved)]
        [TestCase(EnrollmentStatus.Rejected)]
        public async Task EnrollUpdateStatusAsyncTest_Updated(EnrollmentStatus parameter)
        {
            ParticipantEntity participant = new ParticipantEntity();
            CancellationToken cancellation = CancellationToken.None;
            var logger = new Mock<ILogger<HackathonManagement>>();

            ParticipantEntity captured = null;
            var participantTable = new Mock<IParticipantTable>();
            participantTable.Setup(p => p.MergeAsync(It.IsAny<ParticipantEntity>(), cancellation))
                .Callback<ParticipantEntity, CancellationToken>((p, c) =>
                {
                    captured = p;
                });

            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.ParticipantTable).Returns(participantTable.Object);

            var hackathonManagement = new HackathonManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
            };
            await hackathonManagement.EnrollmentUpdateStatusAsync(participant, parameter, cancellation);

            Mock.VerifyAll(storageContext, participantTable, logger);
            participantTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            Assert.IsNotNull(captured);
            Assert.AreEqual(parameter, captured.Status);
            Assert.AreEqual(parameter, participant.Status);
        }
    }
}
