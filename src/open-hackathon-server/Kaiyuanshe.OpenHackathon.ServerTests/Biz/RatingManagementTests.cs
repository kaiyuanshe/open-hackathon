using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Storage;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Kaiyuanshe.OpenHackathon.Server.Storage.Tables;
using Microsoft.Extensions.Logging;
using Moq;
using NUnit.Framework;
using System;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Biz
{
    public class RatingManagementTests
    {
        #region CreateRatingKindAsync
        [TestCase(null, 10)]
        [TestCase(5, 5)]
        public async Task CreateRatingKindAsync(int? maxRating, int expectedMaxRating)
        {
            RatingKind parameter = new RatingKind
            {
                name = "name",
                description = "desc",
                hackathonName = "hack",
                maximumRating = maxRating,
            };

            var logger = new Mock<ILogger<RatingManagement>>();
            var ratingKindTable = new Mock<IRatingKindTable>();
            ratingKindTable.Setup(t => t.InsertAsync(It.Is<RatingKindEntity>(en =>
                en.Name == "name" &&
                en.Description == "desc" &&
                en.PartitionKey == "hack" &&
                en.MaximumRating == expectedMaxRating &&
                !string.IsNullOrWhiteSpace(en.Id) &&
                en.CreatedAt > DateTime.UtcNow.AddMinutes(-1)), default));
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(s => s.RatingKindTable).Returns(ratingKindTable.Object);

            var ratingManagement = new RatingManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
            };
            var result = await ratingManagement.CreateRatingKindAsync(parameter, default);

            Mock.VerifyAll(storageContext, ratingKindTable);
            ratingKindTable.VerifyNoOtherCalls();
            storageContext.VerifyNoOtherCalls();

            Assert.AreEqual("name", result.Name);
            Assert.AreEqual("desc", result.Description);
            Assert.AreEqual("hack", result.HackathonName);
            Assert.AreEqual(expectedMaxRating, result.MaximumRating);
        }
        #endregion
    }
}
