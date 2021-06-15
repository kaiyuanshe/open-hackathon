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
using System.Collections.Generic;
using System.Linq;
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
                tags = new string[] { "a", "b", "c" },
                banners = new PictureInfo[] { new PictureInfo { Name = "pn", Description = "pd", Uri = "pu" } }
            };
            CancellationToken cancellationToken = CancellationToken.None;

            // capture
            HackathonEntity hackInserted = null;
            EnrollmentEntity partInserted = null;

            // mock
            var hackathonTableMock = new Mock<IHackathonTable>();
            hackathonTableMock.Setup(p => p.InsertAsync(It.IsAny<HackathonEntity>(), cancellationToken))
                .Callback<HackathonEntity, CancellationToken>((h, c) => { hackInserted = h; });

            var enrollmentTable = new Mock<IEnrollmentTable>();
            enrollmentTable.Setup(p => p.InsertAsync(It.IsAny<EnrollmentEntity>(), cancellationToken))
                .Callback<EnrollmentEntity, CancellationToken>((h, c) => { partInserted = h; });

            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.HackathonTable).Returns(hackathonTableMock.Object);
            storageContext.SetupGet(p => p.EnrollmentTable).Returns(enrollmentTable.Object);

            // test
            var hackathonManager = new HackathonManagement(null);
            hackathonManager.StorageContext = storageContext.Object;
            var result = await hackathonManager.CreateHackathonAsync(request, CancellationToken.None);

            // verify
            Mock.VerifyAll(hackathonTableMock, enrollmentTable, storageContext);
            hackathonTableMock.VerifyNoOtherCalls();
            enrollmentTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();

            Assert.AreEqual("loc", result.Location);
            Assert.AreEqual("test", result.PartitionKey);
            Assert.AreEqual(string.Empty, result.RowKey);
            Assert.IsTrue(result.EventStartedAt.HasValue);
            Assert.IsFalse(result.EventEndedAt.HasValue);
            Assert.AreEqual("loc", hackInserted.Location);
            Assert.AreEqual(new string[] { "a", "b", "c" }, hackInserted.Tags);
            Assert.AreEqual(1, hackInserted.Banners.Length);
            Assert.AreEqual("pn", hackInserted.Banners[0].Name);
            Assert.AreEqual("pd", hackInserted.Banners[0].Description);
            Assert.AreEqual("pu", hackInserted.Banners[0].Uri);
            Assert.AreEqual("test", partInserted.PartitionKey);
        }

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

            var hackathonManagement = new HackathonManagement(null)
            {
                StorageContext = storageContext.Object
            };
            var updated = await hackathonManagement.UpdateHackathonStatusAsync(hackathonEntity, target, cancellationToken);

            Mock.VerifyAll(storageContext, hackathonTable);
            hackathonTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();

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

            var hackathonTableMock = new Mock<IHackathonTable>();
            hackathonTableMock.Setup(p => p.RetrieveAsync(name, string.Empty, CancellationToken.None))
                .ReturnsAsync(entity);

            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.HackathonTable).Returns(hackathonTableMock.Object);

            var hackathonManager = new HackathonManagement(null);
            hackathonManager.StorageContext = storageContext.Object;
            var result = await hackathonManager.GetHackathonEntityByNameAsync(name, CancellationToken.None);

            Mock.VerifyAll();
            hackathonTableMock.Verify(p => p.RetrieveAsync(name, string.Empty, CancellationToken.None), Times.Once);
            hackathonTableMock.VerifyNoOtherCalls();

            storageContext.VerifyGet(p => p.HackathonTable, Times.Once);
            storageContext.VerifyNoOtherCalls();

            Assert.AreEqual("loc", result.Location);
        }

        #region ListPaginatedHackathonsAsync
        [TestCase(5, 5)]
        [TestCase(-1, 100)]
        public async Task ListPaginatedHackathonsAsync_Options(int topInPara, int expectedTop)
        {
            HackathonQueryOptions options = new HackathonQueryOptions
            {
                TableContinuationToken = new TableContinuationToken { NextPartitionKey = "np", NextRowKey = "nr" },
                Top = topInPara,
            };
            CancellationToken cancellationToken = CancellationToken.None;
            var entities = MockHelper.CreateTableQuerySegment<HackathonEntity>(
                 new List<HackathonEntity>
                 {
                     new HackathonEntity{  PartitionKey="pk" }
                 },
                 new TableContinuationToken { NextPartitionKey = "np2", NextRowKey = "nr2" }
                );

            TableQuery<HackathonEntity> tableQueryCaptured = null;
            TableContinuationToken tableContinuationTokenCapatured = null;

            var logger = new Mock<ILogger<HackathonManagement>>();
            var hackathonTable = new Mock<IHackathonTable>();
            hackathonTable.Setup(p => p.ExecuteQuerySegmentedAsync(It.IsAny<TableQuery<HackathonEntity>>(), It.IsAny<TableContinuationToken>(), cancellationToken))
                .Callback<TableQuery<HackathonEntity>, TableContinuationToken, CancellationToken>((query, c, _) =>
                {
                    tableQueryCaptured = query;
                    tableContinuationTokenCapatured = c;
                })
                .ReturnsAsync(entities);
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.HackathonTable).Returns(hackathonTable.Object);

            var hackathonManagement = new HackathonManagement(logger.Object)
            {
                StorageContext = storageContext.Object
            };
            var segment = await hackathonManagement.ListPaginatedHackathonsAsync(options, cancellationToken);

            Mock.VerifyAll(hackathonTable, storageContext);
            hackathonTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();

            Assert.AreEqual(1, segment.Count());
            Assert.AreEqual("pk", segment.First().Name);
            Assert.AreEqual("np2", segment.ContinuationToken.NextPartitionKey);
            Assert.AreEqual("nr2", segment.ContinuationToken.NextRowKey);
            Assert.AreEqual("np", tableContinuationTokenCapatured.NextPartitionKey);
            Assert.AreEqual("nr", tableContinuationTokenCapatured.NextRowKey);
            Assert.AreEqual("Status eq 2", tableQueryCaptured.FilterString);
            Assert.AreEqual(expectedTop, tableQueryCaptured.TakeCount.Value);
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

            var hackathonManagement = new HackathonManagement(null)
            {
                StorageContext = storageContext.Object,
                Cache = cache,
            };
            var results = await hackathonManagement.ListHackathonAdminAsync(name, cancellationToken);

            Mock.VerifyAll(storageContext, hackAdminTable);
            hackAdminTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            Assert.AreEqual(2, results.Count());
            Assert.AreEqual("pk1", results.First().HackathonName);
            Assert.AreEqual("pk2", results.Last().HackathonName);
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

            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.HackathonTable).Returns(hackathonTableMock.Object);

            var hackathonManager = new HackathonManagement(null);
            hackathonManager.StorageContext = storageContext.Object;
            var result = await hackathonManager.UpdateHackathonAsync(request, CancellationToken.None);

            Mock.VerifyAll();
            hackathonTableMock.Verify(p => p.RetrieveAndMergeAsync(name, string.Empty, It.IsAny<Action<HackathonEntity>>(), CancellationToken.None), Times.Once);
            hackathonTableMock.Verify(p => p.RetrieveAsync(name, string.Empty, CancellationToken.None), Times.Once);
            hackathonTableMock.VerifyNoOtherCalls();

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
