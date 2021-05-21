using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Storage;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Kaiyuanshe.OpenHackathon.Server.Storage.Tables;
using Microsoft.Extensions.Logging;
using Moq;
using NUnit.Framework;
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
            var result = await awardManagement.GeAwardByIdAsync(hackName, awardId, cancellationToken);

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
            var result = await awardManagement.GeAwardByIdAsync(hackName, awardId, cancellationToken);

            Mock.VerifyAll(logger, storageContext, awardTable);
            logger.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            awardTable.VerifyNoOtherCalls();
            Assert.AreEqual("desc", result.Description);
        }

    }
}
