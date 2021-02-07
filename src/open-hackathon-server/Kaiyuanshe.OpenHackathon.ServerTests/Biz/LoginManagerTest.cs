using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Storage;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Kaiyuanshe.OpenHackathon.Server.Storage.Tables;
using Moq;
using NUnit.Framework;
using System;
using System.Collections.Generic;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Biz
{
    [TestFixture]
    public class LoginManagerTest
    {
        [Test]
        public async Task AuthingAsyncTestNew()
        {
            // input
            var loginInfo = new UserLoginInfo
            {
                Id = "id",
                Token = "token",
            };
            var token = new CancellationTokenSource().Token;

            // moc
            var storage = new Mock<IStorageContext>();
            var usertable = new Mock<IUserTable>();
            var tokenTable = new Mock<IUserTokenTable>();
            storage.SetupGet(s => s.UserTable).Returns(usertable.Object);
            storage.SetupGet(s => s.UserTokenTable).Returns(tokenTable.Object);
            usertable.Setup(u => u.RetrieveAsync("id", string.Empty, token)).ReturnsAsync(default(UserEntity));
            usertable.Setup(u => u.InsertAsync(It.IsAny<UserEntity>(), token));
            tokenTable.Setup(t => t.InsertOrReplaceAsync(It.IsAny<UserTokenEntity>(), token));

            // test
            var loginManager = new LoginManager
            {
                StorageContext = storage.Object
            };
            await loginManager.AuthingAsync(loginInfo, token);

            //verify
            Mock.VerifyAll();
            usertable.Verify(u => u.RetrieveAsync("id", string.Empty, token), Times.Exactly(2));
            usertable.Verify(u => u.InsertAsync(It.IsAny<UserEntity>(), token), Times.Once);
            usertable.VerifyNoOtherCalls();
            tokenTable.Verify(t => t.InsertOrReplaceAsync(It.IsAny<UserTokenEntity>(), token), Times.Once);
            tokenTable.VerifyNoOtherCalls();
        }

        [Test]
        public async Task AuthingAsyncTestUpdate()
        {
            // input
            var loginInfo = new UserLoginInfo
            {
                Id = "id",
                Token = "token",
            };
            var token = new CancellationTokenSource().Token;
            var userentity = new UserEntity
            {
                UserName = "name"
            };

            // moc
            var storage = new Mock<IStorageContext>();
            var usertable = new Mock<IUserTable>();
            var tokenTable = new Mock<IUserTokenTable>();
            storage.SetupGet(s => s.UserTable).Returns(usertable.Object);
            storage.SetupGet(s => s.UserTokenTable).Returns(tokenTable.Object);
            usertable.Setup(u => u.RetrieveAsync("id", string.Empty, token)).ReturnsAsync(userentity);
            usertable.Setup(u => u.MergeAsync(userentity, token));
            tokenTable.Setup(t => t.InsertOrReplaceAsync(It.IsAny<UserTokenEntity>(), token));

            // test
            var loginManager = new LoginManager
            {
                StorageContext = storage.Object
            };
            var resp = await loginManager.AuthingAsync(loginInfo, token);

            //verify
            Mock.VerifyAll();
            usertable.Verify(u => u.RetrieveAsync("id", string.Empty, token), Times.Exactly(2));
            usertable.Verify(u => u.MergeAsync(userentity, token), Times.Once);
            usertable.VerifyNoOtherCalls();
            tokenTable.Verify(t => t.InsertOrReplaceAsync(It.IsAny<UserTokenEntity>(), token), Times.Once);
            tokenTable.VerifyNoOtherCalls();
            Assert.AreEqual("name", resp.UserName);
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

            // moc
            var storage = new Mock<IStorageContext>();
            var tokenTable = new Mock<IUserTokenTable>();
            storage.SetupGet(s => s.UserTokenTable).Returns(tokenTable.Object);
            tokenTable.Setup(t => t.RetrieveAsync(hash, string.Empty, cToken)).ReturnsAsync(tokenEntity);

            // test
            var loginManager = new LoginManager
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
    }
}