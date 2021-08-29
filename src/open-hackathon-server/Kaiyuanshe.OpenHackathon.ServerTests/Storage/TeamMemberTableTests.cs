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
    public class TeamMemberTableTests
    {
        [Test]
        public async Task GetMemberCountAsync()
        {
            string hackathonName = "hack";
            string teamId = "tid";

            var awardTable = new Mock<TeamMemberTable> { };
            await awardTable.Object.GetMemberCountAsync(hackathonName, teamId, default);

            awardTable.Verify(t => t.ExecuteQuerySegmentedAsync(
                It.Is<TableQuery<TeamMemberEntity>>(q => q.FilterString == "(PartitionKey eq 'hack') and (TeamId eq 'tid')"
                    && q.SelectColumns.Count == 1
                    && q.SelectColumns.Contains("RowKey")),
                It.IsAny<Action<TableQuerySegment<TeamMemberEntity>>>(),
                default), Times.Once);
            awardTable.VerifyNoOtherCalls();
        }
    }
}
