using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Storage;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Kaiyuanshe.OpenHackathon.Server.Storage.Tables;
using Microsoft.WindowsAzure.Storage.Table;
using Moq;
using NUnit.Framework;
using System;
using System.ComponentModel.DataAnnotations;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Biz
{
    [TestFixture]
    public class UserManagementTest
    {
        [Test]
        public async Task AuthingAsyncTest()
        {
            // input
            var loginInfo = new UserInfo
            {
                Id = "id",
                Token = "token",
            };
            var cancellationToken = new CancellationTokenSource().Token;
            var dynamicEntity = new DynamicTableEntity();

            // moc
            var storage = new Mock<IStorageContext>();
            var usertable = new Mock<IUserTable>();
            var tokenTable = new Mock<IUserTokenTable>();
            storage.SetupGet(s => s.UserTable).Returns(usertable.Object);
            storage.SetupGet(s => s.UserTokenTable).Returns(tokenTable.Object);
            usertable.Setup(u => u.SaveUserAsync(loginInfo, cancellationToken)).ReturnsAsync(dynamicEntity);
            tokenTable.Setup(t => t.InsertOrReplaceAsync(It.IsAny<UserTokenEntity>(), cancellationToken));

            // test
            var loginManager = new UserManagement
            {
                StorageContext = storage.Object
            };
            await loginManager.AuthingAsync(loginInfo, cancellationToken);

            //verify
            Mock.VerifyAll(storage, usertable, tokenTable);
            usertable.VerifyNoOtherCalls();
            tokenTable.VerifyNoOtherCalls();
        }

        [Test]
        public async Task GetTokenEntityAsyncTest()
        {
            // input
            var cToken = new CancellationTokenSource().Token;
            var jwt = "whatever";
            var hash = "ae3d347982977b422948b64011ac14ac76c9ab15898fb562a66a136733aa645fb3a9ccd9bee00cc578c2f44f486af47eb254af7c174244086d174cc52341e63a";
            var tokenEntity = new UserTokenEntity
            {
                UserId = "1",
            };

            // moq
            var storage = new Mock<IStorageContext>();
            var tokenTable = new Mock<IUserTokenTable>();
            storage.SetupGet(s => s.UserTokenTable).Returns(tokenTable.Object);
            tokenTable.Setup(t => t.RetrieveAsync(hash, string.Empty, cToken)).ReturnsAsync(tokenEntity);

            // test
            var loginManager = new UserManagement
            {
                StorageContext = storage.Object,
            };
            var resp = await loginManager.GetTokenEntityAsync(jwt, cToken);

            // verify
            Mock.VerifyAll();
            tokenTable.Verify(t => t.RetrieveAsync(hash, string.Empty, cToken), Times.Once);
            tokenTable.VerifyNoOtherCalls();
            Assert.AreEqual("1", resp.UserId);
        }

        [TestCase(null, "token")]
        [TestCase("", "token")]
        [TestCase("pool", null)]
        [TestCase("pool", "")]
        public void ValidateTokenRemotelyAsyncTest(string userPoolId, string accessToken)
        {
            var loginManager = new UserManagement();
            Assert.ThrowsAsync<ArgumentNullException>(() => loginManager.ValidateTokenRemotelyAsync(userPoolId, accessToken));
        }

        [TestCase(null, "token")]
        [TestCase("", "token")]
        [TestCase("pool", null)]
        [TestCase("pool", "")]
        public void GetCurrentUserRemotelyAsyncTest(string userPoolId, string accessToken)
        {
            var loginManager = new UserManagement();
            Assert.ThrowsAsync<ArgumentNullException>(() => loginManager.GetCurrentUserRemotelyAsync(userPoolId, accessToken));
        }


        [TestCase(null)]
        [TestCase("")]
        [TestCase(" ")]
        public async Task ValidateTokenAsyncTestRequired(string token)
        {
            var loginManager = new UserManagement();
            var result = await loginManager.ValidateTokenAsync(token);

            Assert.AreNotEqual(ValidationResult.Success, result);
            Assert.IsTrue(result.ErrorMessage.Contains("required"));
        }

        [Test]
        public async Task ValidateTokenAsyncTestNotExist()
        {
            // input
            CancellationToken cancellationToken = CancellationToken.None;
            string token = "whatever";
            string hash = "ae3d347982977b422948b64011ac14ac76c9ab15898fb562a66a136733aa645fb3a9ccd9bee00cc578c2f44f486af47eb254af7c174244086d174cc52341e63a";
            UserTokenEntity tokenEntity = null;

            // moq
            var storage = new Mock<IStorageContext>();
            var tokenTable = new Mock<IUserTokenTable>();
            storage.SetupGet(s => s.UserTokenTable).Returns(tokenTable.Object);
            tokenTable.Setup(t => t.RetrieveAsync(hash, string.Empty, cancellationToken)).ReturnsAsync(tokenEntity);

            // testing
            var loginManager = new UserManagement
            {
                StorageContext = storage.Object,
            };
            var result = await loginManager.ValidateTokenAsync(token);

            // verify
            Mock.VerifyAll();
            tokenTable.Verify(t => t.RetrieveAsync(hash, string.Empty, cancellationToken), Times.Once);
            tokenTable.VerifyNoOtherCalls();
            Assert.AreNotEqual(ValidationResult.Success, result);
            Assert.IsTrue(result.ErrorMessage.Contains("doesn't exist"));
        }

        [Test]
        public async Task ValidateTokenAsyncTestExpired()
        {
            // input
            CancellationToken cancellationToken = CancellationToken.None;
            string token = "whatever";
            string hash = "ae3d347982977b422948b64011ac14ac76c9ab15898fb562a66a136733aa645fb3a9ccd9bee00cc578c2f44f486af47eb254af7c174244086d174cc52341e63a";
            UserTokenEntity tokenEntity = new UserTokenEntity
            {
                TokenExpiredAt = DateTime.UtcNow.AddDays(-1),
            };

            // moq
            var storage = new Mock<IStorageContext>();
            var tokenTable = new Mock<IUserTokenTable>();
            storage.SetupGet(s => s.UserTokenTable).Returns(tokenTable.Object);
            tokenTable.Setup(t => t.RetrieveAsync(hash, string.Empty, cancellationToken)).ReturnsAsync(tokenEntity);

            // testing
            var loginManager = new UserManagement
            {
                StorageContext = storage.Object,
            };
            var result = await loginManager.ValidateTokenAsync(token);

            // verify
            Mock.VerifyAll();
            tokenTable.Verify(t => t.RetrieveAsync(hash, string.Empty, cancellationToken), Times.Once);
            tokenTable.VerifyNoOtherCalls();
            Assert.AreNotEqual(ValidationResult.Success, result);
            Assert.IsTrue(result.ErrorMessage.Contains("expired"));
        }

        [Test]
        public async Task ValidateTokenAsyncTestValid()
        {
            // input
            CancellationToken cancellationToken = CancellationToken.None;
            string token = "whatever";
            string hash = "ae3d347982977b422948b64011ac14ac76c9ab15898fb562a66a136733aa645fb3a9ccd9bee00cc578c2f44f486af47eb254af7c174244086d174cc52341e63a";
            UserTokenEntity tokenEntity = new UserTokenEntity
            {
                TokenExpiredAt = DateTime.UtcNow.AddDays(1),
            };

            // moq
            var storage = new Mock<IStorageContext>();
            var tokenTable = new Mock<IUserTokenTable>();
            storage.SetupGet(s => s.UserTokenTable).Returns(tokenTable.Object);
            tokenTable.Setup(t => t.RetrieveAsync(hash, string.Empty, cancellationToken)).ReturnsAsync(tokenEntity);

            // testing
            var loginManager = new UserManagement
            {
                StorageContext = storage.Object,
            };
            var result = await loginManager.ValidateTokenAsync(token);

            // verify
            Mock.VerifyAll();
            tokenTable.Verify(t => t.RetrieveAsync(hash, string.Empty, cancellationToken), Times.Once);
            tokenTable.VerifyNoOtherCalls();
            Assert.AreEqual(ValidationResult.Success, result);
        }
    }
}