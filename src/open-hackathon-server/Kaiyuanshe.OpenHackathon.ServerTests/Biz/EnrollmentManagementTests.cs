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
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Biz
{
    public class EnrollmentManagementTests
    {
        #region CreateEnrollmentAsync
        [TestCase(false, EnrollmentStatus.pendingApproval)]
        [TestCase(true, EnrollmentStatus.approved)]
        public async Task CreateEnrollmentAsync(bool autoApprove, EnrollmentStatus targetStatus)
        {
            HackathonEntity hackathon = new HackathonEntity
            {
                PartitionKey = "hack",
                AutoApprove = autoApprove,
                Enrollment = 5,
            };
            Enrollment request = new Enrollment
            {
                userId = "uid",
                extensions = new Extension[]
                {
                    new Extension { name = "n1", value = "v1" }
                }
            };
            EnrollmentEntity enrollment = null;
            CancellationToken cancellation = CancellationToken.None;
            var logger = new Mock<ILogger<EnrollmentManagement>>();

            var enrollmentTable = new Mock<IEnrollmentTable>();
            enrollmentTable.Setup(p => p.InsertAsync(It.IsAny<EnrollmentEntity>(), cancellation))
                .Callback<EnrollmentEntity, CancellationToken>((p, c) =>
                {
                    enrollment = p;
                });
            var storageContext = new Mock<IStorageContext>();
            var hackathonTable = new Mock<IHackathonTable>();
            storageContext.SetupGet(p => p.EnrollmentTable).Returns(enrollmentTable.Object);
            if (autoApprove)
            {
                hackathonTable.Setup(h => h.MergeAsync(hackathon, cancellation));
                storageContext.SetupGet(s => s.HackathonTable).Returns(hackathonTable.Object);
            }
            var cache = new Mock<ICacheProvider>();

            var enrollmentManagement = new EnrollmentManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
                Cache = cache.Object,
            };
            await enrollmentManagement.CreateEnrollmentAsync(hackathon, request, cancellation);

            Mock.VerifyAll(storageContext, enrollmentTable, hackathonTable);
            enrollmentTable.VerifyNoOtherCalls();
            if (autoApprove)
            {
                hackathonTable.Verify(h => h.MergeAsync(It.Is<HackathonEntity>(h => h.Enrollment == 6), cancellation), Times.Once);
            }
            hackathonTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            cache.Verify(c => c.Remove("Enrollment-hack"), Times.Once);
            cache.VerifyNoOtherCalls();
            Assert.AreEqual(targetStatus, enrollment.Status);
        }
        #endregion

        #region UpdateEnrollmentAsync
        [Test]
        public async Task UpdateEnrollmentAsync()
        {
            EnrollmentEntity existing = new EnrollmentEntity { PartitionKey = "hack" };
            Enrollment request = new Enrollment
            {
                extensions = new Extension[]
                {
                    new Extension { name = "n", value = "v" }
                }
            };

            var enrollmentTable = new Mock<IEnrollmentTable>();
            var storageContext = new Mock<IStorageContext>();
            var hackathonTable = new Mock<IHackathonTable>();
            storageContext.SetupGet(p => p.EnrollmentTable).Returns(enrollmentTable.Object);
            var cache = new Mock<ICacheProvider>();
            cache.Setup(c => c.Remove("Enrollment-hack"));

            var enrollmentManagement = new EnrollmentManagement(null)
            {
                StorageContext = storageContext.Object,
                Cache = cache.Object,
            };
            var result = await enrollmentManagement.UpdateEnrollmentAsync(existing, request, default);

            // verify
            Mock.VerifyAll(enrollmentTable, storageContext, cache);
            enrollmentTable.Verify(e => e.MergeAsync(It.Is<EnrollmentEntity>(en => en.Extensions.Count() == 1 && en.Extensions.First().name == "n" && en.Extensions.First().value == "v"), default), Times.Once);
            enrollmentTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            cache.VerifyNoOtherCalls();

            Assert.AreEqual(1, result.Extensions.Count());
            Assert.AreEqual("n", result.Extensions.First().name);
            Assert.AreEqual("v", result.Extensions.First().value);
        }
        #endregion

        #region UpdateEnrollmentStatusAsync
        [Test]
        public async Task EnrollUpdateStatusAsyncTest_Null()
        {
            HackathonEntity hackathon = null;
            EnrollmentEntity participant = null;
            CancellationToken cancellation = CancellationToken.None;
            var logger = new Mock<ILogger<EnrollmentManagement>>();

            var enrollmentManagement = new EnrollmentManagement(logger.Object);
            await enrollmentManagement.UpdateEnrollmentStatusAsync(hackathon, participant, EnrollmentStatus.approved, cancellation);

            Mock.VerifyAll(logger);
            logger.VerifyNoOtherCalls();
            Assert.IsNull(participant);
        }

        [TestCase(EnrollmentStatus.none, EnrollmentStatus.approved, 1)]
        [TestCase(EnrollmentStatus.pendingApproval, EnrollmentStatus.approved, 1)]
        [TestCase(EnrollmentStatus.approved, EnrollmentStatus.approved, 0)]
        [TestCase(EnrollmentStatus.rejected, EnrollmentStatus.approved, 1)]
        [TestCase(EnrollmentStatus.none, EnrollmentStatus.rejected, 0)]
        [TestCase(EnrollmentStatus.pendingApproval, EnrollmentStatus.rejected, 0)]
        [TestCase(EnrollmentStatus.approved, EnrollmentStatus.rejected, -1)]
        [TestCase(EnrollmentStatus.rejected, EnrollmentStatus.rejected, 0)]
        public async Task EnrollUpdateStatusAsyncTest_Updated(EnrollmentStatus currentStatus, EnrollmentStatus targetStatus, int expectedIncreasement)
        {
            // data
            HackathonEntity hackathon = new HackathonEntity { PartitionKey = "hack", Enrollment = 5 };
            EnrollmentEntity enrollment = new EnrollmentEntity
            {
                Status = currentStatus
            };
            CancellationToken cancellation = CancellationToken.None;

            // setup
            var logger = new Mock<ILogger<EnrollmentManagement>>();
            var storageContext = new Mock<IStorageContext>();
            var enrollmentTable = new Mock<IEnrollmentTable>();
            var cache = new Mock<ICacheProvider>();
            if (currentStatus != targetStatus)
            {
                storageContext.SetupGet(p => p.EnrollmentTable).Returns(enrollmentTable.Object);
                enrollmentTable.Setup(p => p.MergeAsync(It.IsAny<EnrollmentEntity>(), cancellation));
                cache.Setup(c => c.Remove("Enrollment-hack"));
            }
            var hackathonTable = new Mock<IHackathonTable>();
            if (expectedIncreasement != 0)
            {
                storageContext.SetupGet(p => p.HackathonTable).Returns(hackathonTable.Object);
                hackathonTable.Setup(h => h.MergeAsync(hackathon, cancellation));
            }

            // test
            var enrollmentManagement = new EnrollmentManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
                Cache = cache.Object,

            };
            await enrollmentManagement.UpdateEnrollmentStatusAsync(hackathon, enrollment, targetStatus, cancellation);

            // verify
            Mock.VerifyAll(storageContext, enrollmentTable, hackathonTable, logger, cache);
            if (currentStatus != targetStatus)
            {
                enrollmentTable.Verify(p => p.MergeAsync(It.Is<EnrollmentEntity>(p => p.Status == targetStatus), cancellation), Times.Once);
            }
            enrollmentTable.VerifyNoOtherCalls();
            if (expectedIncreasement != 0)
            {
                int expected = 5 + expectedIncreasement;
                hackathonTable.Verify(h => h.MergeAsync(It.Is<HackathonEntity>(h => h.Enrollment == expected), cancellation));
            }
            hackathonTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            cache.VerifyNoOtherCalls();
        }
        #endregion

        #region ListPaginatedEnrollmentsAsync
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

            var logger = new Mock<ILogger<EnrollmentManagement>>();
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

            var enrollmentManagement = new EnrollmentManagement(logger.Object)
            {
                StorageContext = storageContext.Object
            };
            var segment = await enrollmentManagement.ListPaginatedEnrollmentsAsync(hackName, options, cancellationToken);

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

            var logger = new Mock<ILogger<EnrollmentManagement>>();
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

            var enrollmentManagement = new EnrollmentManagement(logger.Object)
            {
                StorageContext = storageContext.Object
            };
            var segment = await enrollmentManagement.ListPaginatedEnrollmentsAsync(hackName, options, cancellationToken);

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
        #endregion

        #region GetEnrollmentAsync
        [TestCase(null, null)]
        [TestCase(null, "uid")]
        [TestCase("hack", null)]
        public async Task GetEnrollmentAsyncTest_NotFound(string hackathon, string userId)
        {
            var enrollmentManagement = new EnrollmentManagement(null);
            var enrollment = await enrollmentManagement.GetEnrollmentAsync(hackathon, userId);
            Assert.IsNull(enrollment);
        }

        [Test]
        public async Task GetEnrollmentAsyncTest_Succeeded()
        {
            EnrollmentEntity participant = new EnrollmentEntity { Status = EnrollmentStatus.rejected };
            CancellationToken cancellation = CancellationToken.None;
            var logger = new Mock<ILogger<EnrollmentManagement>>();

            var enrollmentTable = new Mock<IEnrollmentTable>();
            enrollmentTable.Setup(p => p.RetrieveAsync("hack", "uid", cancellation)).ReturnsAsync(participant);
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.EnrollmentTable).Returns(enrollmentTable.Object);

            var enrollmentManagement = new EnrollmentManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
            };

            var enrollment = await enrollmentManagement.GetEnrollmentAsync("Hack", "uid", cancellation);
            Assert.IsNotNull(enrollment);
            Assert.AreEqual(EnrollmentStatus.rejected, enrollment.Status);
        }
        #endregion

        #region IsUserEnrolledAsync
        [TestCase("anotheruser", EnrollmentStatus.approved, false)]
        [TestCase("uid", EnrollmentStatus.none, false)]
        [TestCase("uid", EnrollmentStatus.pendingApproval, false)]
        [TestCase("uid", EnrollmentStatus.rejected, false)]
        [TestCase("uid", EnrollmentStatus.approved, true)]
        public async Task IsUserEnrolledAsync_Small(string userId, EnrollmentStatus status, bool expectedResult)
        {
            HackathonEntity hackathon = new HackathonEntity { PartitionKey = "hack", MaxEnrollment = 1000 };
            CancellationToken cancellationToken = default;
            IEnumerable<EnrollmentEntity> enrollments = new List<EnrollmentEntity>
            {
                new EnrollmentEntity { RowKey = "uid", Status = status }
            };

            // mock
            var cache = new Mock<ICacheProvider>();
            cache.Setup(c => c.GetOrAddAsync(It.IsAny<CacheEntry<IEnumerable<EnrollmentEntity>>>(), cancellationToken))
                .ReturnsAsync(enrollments);
            var storageContext = new Mock<IStorageContext>();

            // test
            var enrollmentManagement = new EnrollmentManagement(null)
            {
                StorageContext = storageContext.Object,
                Cache = cache.Object,
            };
            var result = await enrollmentManagement.IsUserEnrolledAsync(hackathon, userId, cancellationToken);
            Assert.IsFalse(await enrollmentManagement.IsUserEnrolledAsync(null, userId, cancellationToken));
            Assert.IsFalse(await enrollmentManagement.IsUserEnrolledAsync(hackathon, "", cancellationToken));

            // verify
            cache.Verify(c => c.GetOrAddAsync(It.Is<CacheEntry<IEnumerable<EnrollmentEntity>>>(e => e.AutoRefresh && e.CacheKey == "Enrollment-hack" && e.SlidingExpiration.Hours == 4), cancellationToken), Times.Once);
            cache.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            Assert.AreEqual(expectedResult, result);
        }

        private static IEnumerable IsUserEnrolledAsync_Big_TestData()
        {
            // arg0: max enrollment
            // arg1: EnrollmentEntity
            // arg2: expected result

            // empty
            yield return new TestCaseData(
                1001,
                null,
                false);

            // unapproved
            yield return new TestCaseData(
                -1,
                new EnrollmentEntity { Status = EnrollmentStatus.none },
                false);
            yield return new TestCaseData(
                -1,
                new EnrollmentEntity { Status = EnrollmentStatus.pendingApproval },
                false);
            yield return new TestCaseData(
                -1,
                new EnrollmentEntity { Status = EnrollmentStatus.rejected },
                false);

            // approved
            yield return new TestCaseData(
                10000,
                new EnrollmentEntity { Status = EnrollmentStatus.approved },
                true);
        }

        [Test, TestCaseSource(nameof(IsUserEnrolledAsync_Big_TestData))]
        public async Task IsUserEnrolledAsync_Big(int maxEnrollment, EnrollmentEntity enrollment, bool expectedResult)
        {
            HackathonEntity hackathon = new HackathonEntity { PartitionKey = "hack", MaxEnrollment = maxEnrollment };
            string userId = "uid";
            CancellationToken cancellationToken = default;

            // mock
            var cache = new Mock<ICacheProvider>();
            var storageContext = new Mock<IStorageContext>();
            var enrollmentTable = new Mock<IEnrollmentTable>();
            enrollmentTable.Setup(p => p.RetrieveAsync("hack", userId, cancellationToken)).ReturnsAsync(enrollment);
            storageContext.SetupGet(p => p.EnrollmentTable).Returns(enrollmentTable.Object);

            // test
            var enrollmentManagement = new EnrollmentManagement(null)
            {
                StorageContext = storageContext.Object,
                Cache = cache.Object,
            };
            var result = await enrollmentManagement.IsUserEnrolledAsync(hackathon, userId, cancellationToken);

            // verify
            Mock.VerifyAll(cache, storageContext, enrollmentTable);
            cache.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            enrollmentTable.VerifyNoOtherCalls();

            Assert.AreEqual(expectedResult, result);
        }
        #endregion
    }
}
