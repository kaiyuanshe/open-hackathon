using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Cache;
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
    public class JudgeManagementTests
    {
        #region CreateJudgeAsync
        [Test]
        public async Task CreateJudgeAsync()
        {
            Judge parameter = new Judge
            {
                hackathonName = "hack",
                description = "desc",
                userId = "uid"
            };

            var logger = new Mock<ILogger<JudgeManagement>>();
            var judgeTable = new Mock<IJudgeTable>();
            judgeTable.Setup(j => j.InsertOrReplaceAsync(It.Is<JudgeEntity>(en =>
                en.Description == "desc" &&
                en.PartitionKey == "hack" &&
                en.HackathonName == "hack" &&
                en.RowKey == "uid" &&
                en.UserId == "uid"), default));
            var storageContext = new Mock<IStorageContext>();
            storageContext.Setup(s => s.JudgeTable).Returns(judgeTable.Object);
            var cache = new Mock<ICacheProvider>();
            cache.Setup(c => c.Remove("Judge-hack"));

            var judgeManagement = new JudgeManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
                Cache = cache.Object,
            };
            var result = await judgeManagement.CreateJudgeAsync(parameter, default);

            Mock.VerifyAll(judgeTable, storageContext, cache);
            judgeTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();
            cache.VerifyNoOtherCalls();

            Assert.AreEqual("desc", result.Description);
            Assert.AreEqual("hack", result.HackathonName);
            Assert.AreEqual("uid", result.UserId);
        }
        #endregion

        #region GetJudgeAsync
        [Test]
        public async Task GetJudgeAsync()
        {
            var judge = new JudgeEntity { PartitionKey = "pk" };

            var logger = new Mock<ILogger<JudgeManagement>>();
            var judgeTable = new Mock<IJudgeTable>();
            judgeTable.Setup(j => j.RetrieveAsync("hack", "uid", default)).ReturnsAsync(judge);
            var storageContext = new Mock<IStorageContext>();
            storageContext.Setup(s => s.JudgeTable).Returns(judgeTable.Object);

            var judgeManagement = new JudgeManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
            };
            var result = await judgeManagement.GetJudgeAsync("hack", "uid", default);

            Mock.VerifyAll(judgeTable, storageContext);
            judgeTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();

            Assert.AreEqual("pk", result.HackathonName);
        }
        #endregion
    }
}
