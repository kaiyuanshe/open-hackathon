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
                            new PictureInfo{ Name="p1", Description="d1", Uri="u1" },
                            new PictureInfo{ Name="p2", Description="d2", Uri="u2" },
                            new PictureInfo{ Name="p3", Description="d3", Uri="u3" },
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
                            new PictureInfo{ Name="p1", Description="d1", Uri="u1" },
                            new PictureInfo{ Name="p2", Description="d2", Uri="u2" },
                            new PictureInfo{ Name="p3", Description="d3", Uri="u3" },
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

            AwardManagement awardManagement = new AwardManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
            };
            var result = await awardManagement.CreateAwardAsync(hackName, request, cancellationToken);

            Mock.VerifyAll(logger, storageContext, awardTable);
            logger.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            awardTable.VerifyNoOtherCalls();

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
                Assert.AreEqual(expectedEntity.Pictures[0].Uri, result.Pictures[0].Uri);
                Assert.AreEqual(expectedEntity.Pictures[0].Name, result.Pictures[0].Name);
                Assert.AreEqual(expectedEntity.Pictures[0].Description, result.Pictures[0].Description);
            }
        }

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
                            new PictureInfo{ Name="p1", Description="d1", Uri="u1" },
                            new PictureInfo{ Name="p2", Description="d2", Uri="u2" },
                            new PictureInfo{ Name="p3", Description="d3", Uri="u3" },
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
                            new PictureInfo{ Name="p1", Description="d1", Uri="u1" },
                            new PictureInfo{ Name="p2", Description="d2", Uri="u2" },
                            new PictureInfo{ Name="p3", Description="d3", Uri="u3" },
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
                            new PictureInfo{ Name="p4", Description="d4", Uri="u4" },
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
                            new PictureInfo{ Name="p1", Description="d1", Uri="u1" },
                            new PictureInfo{ Name="p2", Description="d2", Uri="u2" },
                            new PictureInfo{ Name="p3", Description="d3", Uri="u3" },
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
                            new PictureInfo{ Name="p4", Description="d4", Uri="u4" },
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

            AwardManagement awardManagement = new AwardManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
            };
            var result = await awardManagement.UpdateAwardAsync(existing, request, cancellationToken);

            Mock.VerifyAll(logger, storageContext, awardTable);
            logger.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            awardTable.VerifyNoOtherCalls();

            Assert.AreEqual(expectedEntity.Description, result.Description);
            Assert.AreEqual(expectedEntity.Name, result.Name);
            Assert.AreEqual(expectedEntity.Quantity, result.Quantity);
            Assert.AreEqual(expectedEntity.Target, result.Target);
            Assert.AreEqual(expectedEntity.Pictures?.Length, result.Pictures?.Length);
            for (int i = 0; i < result.Pictures?.Length; i++)
            {
                Assert.AreEqual(expectedEntity.Pictures[0].Uri, result.Pictures[0].Uri);
                Assert.AreEqual(expectedEntity.Pictures[0].Name, result.Pictures[0].Name);
                Assert.AreEqual(expectedEntity.Pictures[0].Description, result.Pictures[0].Description);
            }
        }

        #region ListPaginatedAwardsAsync

        private static IEnumerable ListPaginatedAwardsAsyncTestData()
        {
            // arg0: options
            // arg1: expected top
            // arg2: expected query

            // no options
            yield return new TestCaseData(
                null,
                100,
                "PartitionKey eq 'foo'"
                );

            // top
            yield return new TestCaseData(
                new AwardQueryOptions { Top = 5 },
                5,
                "PartitionKey eq 'foo'"
                );
            yield return new TestCaseData(
               new AwardQueryOptions { Top = -1 },
               100,
               "PartitionKey eq 'foo'"
               );
        }

        [Test, TestCaseSource(nameof(ListPaginatedAwardsAsyncTestData))]
        public async Task ListPaginatedAwardsAsync_Options(AwardQueryOptions options, int expectedTop, string expectedFilter)
        {
            string hackName = "foo";
            CancellationToken cancellationToken = CancellationToken.None;
            var entities = MockHelper.CreateTableQuerySegment<AwardEntity>(
                 new List<AwardEntity>
                 {
                     new AwardEntity{  PartitionKey="pk" }
                 },
                 new TableContinuationToken { NextPartitionKey = "np", NextRowKey = "nr" }
                );

            TableQuery<AwardEntity> tableQueryCaptured = null;
            TableContinuationToken tableContinuationTokenCapatured = null;

            var logger = new Mock<ILogger<AwardManagement>>();
            var awardTable = new Mock<IAwardTable>();
            awardTable.Setup(p => p.ExecuteQuerySegmentedAsync(It.IsAny<TableQuery<AwardEntity>>(), It.IsAny<TableContinuationToken>(), cancellationToken))
                .Callback<TableQuery<AwardEntity>, TableContinuationToken, CancellationToken>((query, c, _) =>
                {
                    tableQueryCaptured = query;
                    tableContinuationTokenCapatured = c;
                })
                .ReturnsAsync(entities);
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.AwardTable).Returns(awardTable.Object);

            var awardManagement = new AwardManagement(logger.Object)
            {
                StorageContext = storageContext.Object
            };
            var segment = await awardManagement.ListPaginatedAwardsAsync(hackName, options, cancellationToken);

            Mock.VerifyAll(awardTable, storageContext);
            awardTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();

            Assert.AreEqual(1, segment.Count());
            Assert.AreEqual("pk", segment.First().HackathonName);
            Assert.AreEqual("np", segment.ContinuationToken.NextPartitionKey);
            Assert.AreEqual("nr", segment.ContinuationToken.NextRowKey);
            Assert.IsNull(tableContinuationTokenCapatured);
            Assert.AreEqual(expectedFilter, tableQueryCaptured.FilterString);
            Assert.AreEqual(expectedTop, tableQueryCaptured.TakeCount.Value);
        }
        #endregion
    }
}
