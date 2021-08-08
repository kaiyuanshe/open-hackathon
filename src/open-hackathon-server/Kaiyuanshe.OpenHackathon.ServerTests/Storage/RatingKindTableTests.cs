using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Kaiyuanshe.OpenHackathon.Server.Storage.Tables;
using Microsoft.WindowsAzure.Storage.Table;
using Moq;
using NUnit.Framework;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Storage
{
    public class RatingKindTableTests
    {
        #region ListRatingKindsAsync
        [Test]
        public async Task ListRatingKindsAsync()
        {
            string hackathonName = "hack";

            var ratingKindTable = new Mock<RatingKindTable> { };
            await ratingKindTable.Object.ListRatingKindsAsync(hackathonName, default);

            ratingKindTable.Verify(t => t.ExecuteQuerySegmentedAsync(
                It.Is<TableQuery<RatingKindEntity>>(q => q.FilterString == "PartitionKey eq 'hack'"),
                It.IsAny<Action<TableQuerySegment<RatingKindEntity>>>(),
                default), Times.Once);
            ratingKindTable.VerifyNoOtherCalls();
        }
        #endregion
    }
}
