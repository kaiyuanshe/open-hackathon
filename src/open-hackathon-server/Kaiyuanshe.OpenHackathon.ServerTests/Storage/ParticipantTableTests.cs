using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Kaiyuanshe.OpenHackathon.Server.Storage.Tables;
using Kaiyuanshe.OpenHackathon.Servers;
using Microsoft.WindowsAzure.Storage.Table;
using Moq;
using NUnit.Framework;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Storage
{
    [TestFixture]
    public class ParticipantTableTests
    {
        [Test]
        public async Task ListParticipantsByHackathonAsyncTest()
        {
            var table = new Mock<ParticipantTable> { CallBase = true };

            CancellationToken cancellationToken = CancellationToken.None;
            List<ParticipantEntity> participants = new List<ParticipantEntity>
            {
                new ParticipantEntity{ PartitionKey="pk1" },
                new ParticipantEntity{}
            };
            var querySegment = MockHelper.CreateTableQuerySegment(participants, null);
            table.Setup(t => t.ExecuteQuerySegmentedAsync(It.IsAny<TableQuery<ParticipantEntity>>(), It.IsAny<Action<TableQuerySegment<ParticipantEntity>>>(), cancellationToken))
                .Callback<TableQuery<ParticipantEntity>, Action<TableQuerySegment<ParticipantEntity>>, CancellationToken>((query, action, token) => { action(querySegment); })
                .Returns(Task.CompletedTask);

            var results = await table.Object.ListParticipantsByHackathonAsync("", cancellationToken);
            Assert.AreEqual(2, results.Count());
            Assert.AreEqual("pk1", results.First().HackathonName);
        }
    }
}
