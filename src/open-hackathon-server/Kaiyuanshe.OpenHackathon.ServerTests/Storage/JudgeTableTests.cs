using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Kaiyuanshe.OpenHackathon.Server.Storage.Tables;
using Microsoft.WindowsAzure.Storage.Table;
using Moq;
using NUnit.Framework;
using System;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Storage
{
    public class JudgeTableTests
    {
        #region ListByHackathonAsync
        [Test]
        public async Task ListByHackathonAsync()
        {
            string hackathonName = "hack";

            var judgeTable = new Mock<JudgeTable> { };
            await judgeTable.Object.ListByHackathonAsync(hackathonName, default);

            judgeTable.Verify(t => t.ExecuteQuerySegmentedAsync(
                It.Is<TableQuery<JudgeEntity>>(q => q.FilterString == "PartitionKey eq 'hack'"),
                It.IsAny<Action<TableQuerySegment<JudgeEntity>>>(),
                default), Times.Once);
            judgeTable.VerifyNoOtherCalls();
        }
        #endregion
    }
}
