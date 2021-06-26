using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Kaiyuanshe.OpenHackathon.Server.Storage.Tables;
using Microsoft.WindowsAzure.Storage.Table;
using Moq;
using NUnit.Framework;
using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Storage
{
    public class AwardTableTests
    {
        [Test]
        public async Task ListAllAwardsAsync()
        {
            string hackathonName = "hack";

            var awardTable = new Mock<AwardTable> { };
            await awardTable.Object.ListAllAwardsAsync(hackathonName, default);

            awardTable.Verify(t => t.ExecuteQuerySegmentedAsync(
                It.Is<TableQuery<AwardEntity>>(q => q.FilterString == "PartitionKey eq 'hack'"),
                It.IsAny<Action<TableQuerySegment<AwardEntity>>>(),
                default), Times.Once);
            awardTable.VerifyNoOtherCalls();
        }
    }
}
