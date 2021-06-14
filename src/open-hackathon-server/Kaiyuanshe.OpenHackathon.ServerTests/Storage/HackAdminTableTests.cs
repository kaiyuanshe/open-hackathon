using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Kaiyuanshe.OpenHackathon.Server.Storage.Tables;
using Microsoft.WindowsAzure.Storage.Table;
using Moq;
using NUnit.Framework;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Storage
{
    [TestFixture]
    public class HackAdminTableTests
    {
        [Test]
        public async Task ListParticipantsByHackathonAsyncTest()
        {
            var table = new Mock<HackathonAdminTable> { CallBase = true };

            CancellationToken cancellationToken = CancellationToken.None;
            List<HackathonAdminEntity> participants = new List<HackathonAdminEntity>
            {
                new HackathonAdminEntity{ PartitionKey="pk1" },
                new HackathonAdminEntity{}
            };
            var querySegment = MockHelper.CreateTableQuerySegment(participants, null);
            table.Setup(t => t.ExecuteQuerySegmentedAsync(It.IsAny<TableQuery<HackathonAdminEntity>>(), It.IsAny<Action<TableQuerySegment<HackathonAdminEntity>>>(), cancellationToken))
                .Callback<TableQuery<HackathonAdminEntity>, Action<TableQuerySegment<HackathonAdminEntity>>, CancellationToken>((query, action, token) => { action(querySegment); })
                .Returns(Task.CompletedTask);

            var results = await table.Object.ListByHackathonAsync("", cancellationToken);
            Assert.AreEqual(2, results.Count());
            Assert.AreEqual("pk1", results.First().HackathonName);
        }
    }
}
