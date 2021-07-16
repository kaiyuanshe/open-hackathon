using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Storage;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Kaiyuanshe.OpenHackathon.Server.Storage.Tables;
using Microsoft.Extensions.Logging;
using Moq;
using NUnit.Framework;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Biz
{
    public class WorkManagementTests
    {
        #region CreateTeamWorkAsync
        [TestCase(null)]
        [TestCase(TeamWorkType.video)]
        public async Task CreateTeamWorkAsync(TeamWorkType? type)
        {
            // input
            TeamWork request = new TeamWork
            {
                description = "desc",
                hackathonName = "hack",
                teamId = "teamId",
                title = "title",
                type = type,
                url = "url"
            };

            // mock
            var logger = new Mock<ILogger<WorkManagement>>();
            var teamWorkTable = new Mock<ITeamWorkTable>();
            teamWorkTable.Setup(p => p.InsertAsync(It.Is<TeamWorkEntity>(e => e.Description == "desc"
                && e.HackathonName == "hack"
                && e.TeamId == "teamId"
                && e.Title == "title"
                && e.Url == "url"
                && e.Type == type.GetValueOrDefault(TeamWorkType.website)), default));
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.TeamWorkTable).Returns(teamWorkTable.Object);

            // test
            var workManagement = new WorkManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
            };
            var result = await workManagement.CreateTeamWorkAsync(request, default);


            // verify
            Mock.VerifyAll(teamWorkTable, storageContext);
            teamWorkTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
        }
        #endregion

        #region GetTeamWorkAsync
        [Test]
        public async Task GetTeamWorkAsync()
        {
            var teamWork = new TeamWorkEntity { HackathonName = "hack" };

            // mock
            var logger = new Mock<ILogger<WorkManagement>>();
            var teamWorkTable = new Mock<ITeamWorkTable>();
            teamWorkTable.Setup(p => p.RetrieveAsync("tid", "wid", default)).ReturnsAsync(teamWork);
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.TeamWorkTable).Returns(teamWorkTable.Object);

            // test
            var workManagement = new WorkManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
            };
            var result = await workManagement.GetTeamWorkAsync("tid", "wid", default);

            // verify
            Mock.VerifyAll(teamWorkTable, storageContext);
            teamWorkTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            Assert.AreEqual("hack", result.HackathonName);
        }
        #endregion
    }
}
