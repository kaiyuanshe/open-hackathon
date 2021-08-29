using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Kaiyuanshe.OpenHackathon.Server.Storage.Tables;
using Microsoft.WindowsAzure.Storage.Table;
using Moq;
using NUnit.Framework;
using System;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Storage
{
    public class TeamWorkTableTests
    {
        [Test]
        public async Task ListByTeamAsync()
        {
            var teamWorkTable = new Mock<TeamWorkTable> { };
            await teamWorkTable.Object.ListByTeamAsync("hack", "tid", default);

            teamWorkTable.Verify(t => t.ExecuteQuerySegmentedAsync(
                It.Is<TableQuery<TeamWorkEntity>>(q => q.FilterString == "(PartitionKey eq 'hack') and (TeamId eq 'tid')"),
                It.IsAny<Action<TableQuerySegment<TeamWorkEntity>>>(),
                default), Times.Once);
            teamWorkTable.VerifyNoOtherCalls();
        }
    }
}
