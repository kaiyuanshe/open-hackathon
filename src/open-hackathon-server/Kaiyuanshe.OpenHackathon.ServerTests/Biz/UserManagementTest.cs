using Kaiyuanshe.OpenHackathon.Server.Auth;
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
using System.Linq;
using System.Security.Claims;
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
            var userInfo = new UserInfo
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
            usertable.Setup(u => u.SaveUserAsync(userInfo, cancellationToken)).ReturnsAsync(dynamicEntity);
            tokenTable.Setup(t => t.InsertOrReplaceAsync(It.IsAny<UserTokenEntity>(), cancellationToken));

            // test
            var userMgmt = new UserManagement
            {
                StorageContext = storage.Object
            };
            await userMgmt.AuthingAsync(userInfo, cancellationToken);

            //verify
            Mock.VerifyAll(storage, usertable, tokenTable);
            usertable.VerifyNoOtherCalls();
            tokenTable.VerifyNoOtherCalls();
        }

        [TestCase(null, "token")]
        [TestCase("", "token")]
        [TestCase("pool", null)]
        [TestCase("pool", "")]
        public void GetCurrentUserRemotelyAsyncTest(string userPoolId, string accessToken)
        {
            var userMgmt = new UserManagement();
            Assert.ThrowsAsync<ArgumentNullException>(() => userMgmt.GetCurrentUserRemotelyAsync(userPoolId, accessToken));
        }

        [Test]
        public async Task GetCurrentUserClaimsAsyncTestInvalidToken1()
        {
            string token = "token";
            CancellationToken cancellationToken = CancellationToken.None;
            UserTokenEntity tokenEntity = null;

            var userMgmtMock = new Mock<UserManagement> { CallBase = true };
            userMgmtMock.Setup(m => m.GetTokenEntityAsync(token, cancellationToken)).ReturnsAsync(tokenEntity);

            var claims = await userMgmtMock.Object.GetCurrentUserClaimsAsync(token, cancellationToken);

            Mock.VerifyAll(userMgmtMock);
            Assert.AreEqual(0, claims.Count());
        }

        [Test]
        public async Task GetCurrentUserClaimsAsyncTestInvalidToken2()
        {
            string token = "token";
            CancellationToken cancellationToken = CancellationToken.None;
            UserTokenEntity tokenEntity = new UserTokenEntity
            {
                TokenExpiredAt = DateTime.UtcNow.AddMinutes(-1)
            };

            var userMgmtMock = new Mock<UserManagement> { CallBase = true };
            userMgmtMock.Setup(m => m.GetTokenEntityAsync(token, cancellationToken)).ReturnsAsync(tokenEntity);

            var claims = await userMgmtMock.Object.GetCurrentUserClaimsAsync(token, cancellationToken);

            Mock.VerifyAll(userMgmtMock);
            Assert.AreEqual(0, claims.Count());
        }

        [Test]
        public async Task GetCurrentUserClaimsAsyncTestPlatformAdmin()
        {
            string token = "token";
            string userId = "userid";
            CancellationToken cancellationToken = CancellationToken.None;
            UserTokenEntity tokenEntity = new UserTokenEntity
            {
                TokenExpiredAt = DateTime.UtcNow.AddMinutes(1),
                UserId = userId,
            };
            Claim claim = new Claim("type", "value", "valueType", "issuer");

            var userMgmtMock = new Mock<UserManagement> { CallBase = true };
            userMgmtMock.Setup(m => m.GetTokenEntityAsync(token, cancellationToken)).ReturnsAsync(tokenEntity);
            userMgmtMock.Setup(m => m.GetPlatformRoleClaim(userId, cancellationToken)).ReturnsAsync(claim);

            var claims = await userMgmtMock.Object.GetCurrentUserClaimsAsync(token, cancellationToken);

            Mock.VerifyAll(userMgmtMock);
            Assert.AreEqual(2, claims.Count());

            // user id
            Assert.AreEqual(AuthConstant.ClaimType.UserId, claims.First().Type);
            Assert.AreEqual(userId, claims.First().Value);
            Assert.AreEqual(ClaimValueTypes.String, claims.First().ValueType);
            Assert.AreEqual(AuthConstant.Issuer.Default, claims.First().Issuer);

            // platform admin
            Assert.AreEqual("type", claims.Last().Type);
            Assert.AreEqual("value", claims.Last().Value);
            Assert.AreEqual("valueType", claims.Last().ValueType);
            Assert.AreEqual("issuer", claims.Last().Issuer);
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
            var userMgmt = new UserManagement
            {
                StorageContext = storage.Object,
            };
            var resp = await userMgmt.GetTokenEntityAsync(jwt, cToken);

            // verify
            Mock.VerifyAll();
            tokenTable.Verify(t => t.RetrieveAsync(hash, string.Empty, cToken), Times.Once);
            tokenTable.VerifyNoOtherCalls();
            Assert.AreEqual("1", resp.UserId);
        }

        [TestCase(null)]
        [TestCase("")]
        [TestCase(" ")]
        public async Task ValidateTokenAsyncTestRequired(string token)
        {
            var userMgmt = new UserManagement();
            var result = await userMgmt.ValidateTokenAsync(token);

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
            var userMgmt = new UserManagement
            {
                StorageContext = storage.Object,
            };
            var result = await userMgmt.ValidateTokenAsync(token);

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
            var userMgmt = new UserManagement
            {
                StorageContext = storage.Object,
            };
            var result = await userMgmt.ValidateTokenAsync(token);

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
            var userMgmt = new UserManagement
            {
                StorageContext = storage.Object,
            };
            var result = await userMgmt.ValidateTokenAsync(token);

            // verify
            Mock.VerifyAll();
            tokenTable.Verify(t => t.RetrieveAsync(hash, string.Empty, cancellationToken), Times.Once);
            tokenTable.VerifyNoOtherCalls();
            Assert.AreEqual(ValidationResult.Success, result);
        }

        [Test]
        public async Task TaskValidateTokenAsyncTestEntityNull()
        {
            UserTokenEntity tokenEntity = null;
            CancellationToken cancellationToken = CancellationToken.None;

            var userMgmt = new UserManagement();
            var validationResult = await userMgmt.ValidateTokenAsync(tokenEntity, cancellationToken);

            Assert.AreNotEqual(ValidationResult.Success, validationResult);
            Assert.IsTrue(validationResult.ErrorMessage.Contains("doesn't exist"));
        }

        [Test]
        public async Task TaskValidateTokenAsyncTestEntityExpired()
        {
            UserTokenEntity tokenEntity = new UserTokenEntity { TokenExpiredAt = DateTime.UtcNow.AddMinutes(-1) };
            CancellationToken cancellationToken = CancellationToken.None;

            var userMgmt = new UserManagement();
            var validationResult = await userMgmt.ValidateTokenAsync(tokenEntity, cancellationToken);

            Assert.AreNotEqual(ValidationResult.Success, validationResult);
            Assert.IsTrue(validationResult.ErrorMessage.Contains("expired"));
        }

        [Test]
        public async Task TaskValidateTokenAsyncTestEntityValid()
        {
            UserTokenEntity tokenEntity = new UserTokenEntity { TokenExpiredAt = DateTime.UtcNow.AddHours(1) };
            CancellationToken cancellationToken = CancellationToken.None;

            var userMgmt = new UserManagement();
            var validationResult = await userMgmt.ValidateTokenAsync(tokenEntity, cancellationToken);

            Assert.AreEqual(ValidationResult.Success, validationResult);
        }

        [TestCase(null, "token")]
        [TestCase("", "token")]
        [TestCase("pool", null)]
        [TestCase("pool", "")]
        public void ValidateTokenRemotelyAsyncTest(string userPoolId, string accessToken)
        {
            var userMgmt = new UserManagement();
            Assert.ThrowsAsync<ArgumentNullException>(() => userMgmt.ValidateTokenRemotelyAsync(userPoolId, accessToken));
        }

        [Test]
        public async Task GetPlatformRoleClaimTestEnityNotFound()
        {
            // input
            CancellationToken cancellationToken = CancellationToken.None;
            string userId = "userid";
            ParticipantEntity entity = null;

            // moq
            var storage = new Mock<IStorageContext>();
            var participantTable = new Mock<IParticipantTable>();
            storage.SetupGet(s => s.ParticipantTable).Returns(participantTable.Object);
            participantTable.Setup(t => t.GetPlatformRole(userId, cancellationToken)).ReturnsAsync(entity);

            // test
            var userMgmt = new UserManagement
            {
                StorageContext = storage.Object,
            };
            var claim = await userMgmt.GetPlatformRoleClaim(userId, cancellationToken);

            // verify
            Mock.VerifyAll(storage, participantTable);
            Assert.IsNull(claim);
        }

        [TestCase("pk", ParticipantRole.Administrator)]
        [TestCase("", ParticipantRole.Contestant)]
        [TestCase("", ParticipantRole.Judge)]
        [TestCase("", ParticipantRole.None)]
        public async Task GetPlatformRoleClaimTestNotAdmin(string pk, ParticipantRole role)
        {
            // input
            CancellationToken cancellationToken = CancellationToken.None;
            string userId = "userid";
            ParticipantEntity entity = new ParticipantEntity
            {
                PartitionKey = pk,
                Role = role
            };

            // moq
            var storage = new Mock<IStorageContext>();
            var participantTable = new Mock<IParticipantTable>();
            storage.SetupGet(s => s.ParticipantTable).Returns(participantTable.Object);
            participantTable.Setup(t => t.GetPlatformRole(userId, cancellationToken)).ReturnsAsync(entity);

            // test
            var userMgmt = new UserManagement
            {
                StorageContext = storage.Object,
            };
            var claim = await userMgmt.GetPlatformRoleClaim(userId, cancellationToken);

            // verify
            Mock.VerifyAll(storage, participantTable);
            Assert.IsNull(claim);
        }

        [Test]
        public async Task GetPlatformRoleClaimTestValidClaim()
        {
            // input
            CancellationToken cancellationToken = CancellationToken.None;
            string userId = "userid";
            ParticipantEntity entity = new ParticipantEntity
            {
                Role = ParticipantRole.Administrator
            };

            // moq
            var storage = new Mock<IStorageContext>();
            var participantTable = new Mock<IParticipantTable>();
            storage.SetupGet(s => s.ParticipantTable).Returns(participantTable.Object);
            participantTable.Setup(t => t.GetPlatformRole(userId, cancellationToken)).ReturnsAsync(entity);

            // test
            var userMgmt = new UserManagement
            {
                StorageContext = storage.Object,
            };
            var claim = await userMgmt.GetPlatformRoleClaim(userId, cancellationToken);

            // verify
            Mock.VerifyAll(storage, participantTable);
            Assert.IsNotNull(claim);
            Assert.AreEqual(AuthConstant.ClaimType.PlatformAdministrator, claim.Type);
            Assert.AreEqual(userId, claim.Value);
            Assert.AreEqual(ClaimValueTypes.String, claim.ValueType);
            Assert.AreEqual(AuthConstant.Issuer.Default, claim.Issuer);

        }
    }
}