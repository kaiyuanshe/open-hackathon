using Authing.ApiClient.Types;
using Kaiyuanshe.OpenHackathon.Server;
using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Controllers;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.ResponseBuilder;
using Moq;
using NUnit.Framework;
using System.Security.Claims;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Controllers
{
    [TestFixture]
    public class UserControllerTests
    {
        #region AuthingTestWithInvalidToken
        [Test]
        public async Task AuthingTestWithInvalidToken()
        {
            // input
            var parameter = new UserInfo { Token = "token", UserPoolId = "pool" };
            var cancellationToken = CancellationToken.None;
            var jwtTokenStatus = new JWTTokenStatus { Status = false, Code = 400, Message = "Some Message" };

            // Moq
            var loginManagerMoq = new Mock<IUserManagement>();
            loginManagerMoq.Setup(p => p.ValidateTokenRemotelyAsync("pool", "token", cancellationToken)).ReturnsAsync(jwtTokenStatus);

            // test
            var controller = new UserController
            {
                UserManagement = loginManagerMoq.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var resp = await controller.Authing(parameter, cancellationToken);

            // Verify
            Mock.VerifyAll(loginManagerMoq);
            loginManagerMoq.VerifyNoOtherCalls();

            AssertHelper.AssertObjectResult(resp, 400, p =>
            {
                Assert.IsTrue(p.Detail.Contains("Some Message"));
            });
        }
        #endregion

        #region GetUserById
        [Test]
        public async Task GetUserById_NotFound()
        {
            string userId = "uid";
            CancellationToken cancellationToken = CancellationToken.None;
            UserInfo userInfo = null;

            // mock
            var userManagement = new Mock<IUserManagement>();
            userManagement.Setup(u => u.GetUserByIdAsync(userId, cancellationToken))
                .ReturnsAsync(userInfo);

            // test
            var controller = new UserController
            {
                UserManagement = userManagement.Object,
                ProblemDetailsFactory = new CustomProblemDetailsFactory(),
            };
            var result = await controller.GetUserById(userId, cancellationToken);

            // verify
            Mock.VerifyAll(userManagement);
            userManagement.VerifyNoOtherCalls();

            AssertHelper.AssertObjectResult(result, 404, Resources.User_NotFound);
        }

        [Test]
        public async Task GetUserById()
        {
            string userId = "uid";
            CancellationToken cancellationToken = CancellationToken.None;
            UserInfo userInfo = new UserInfo { };

            // mock
            var userManagement = new Mock<IUserManagement>();
            userManagement.Setup(u => u.GetUserByIdAsync(userId, cancellationToken))
                .ReturnsAsync(userInfo);

            // test
            var controller = new UserController
            {
                UserManagement = userManagement.Object,
            };
            var result = await controller.GetUserById(userId, cancellationToken);

            // verify
            Mock.VerifyAll(userManagement);
            userManagement.VerifyNoOtherCalls();
            var resp = AssertHelper.AssertOKResult<UserInfo>(result);
            Assert.AreEqual(resp, userInfo);
        }

        #endregion

        #region GetUploadUrl
        [Test]
        public async Task GetUploadUrl()
        {
            // input
            var parameter = new FileUpload { };
            var uploaded = new FileUpload { expiration = 10, filename = "user/avatar.jpg" };

            // mock
            var fileManagement = new Mock<IFileManagement>();
            fileManagement.Setup(u => u.GetUploadUrlAsync(It.IsAny<ClaimsPrincipal>(), parameter, default)).ReturnsAsync(uploaded);

            // test
            var controller = new UserController
            {
                FileManagement = fileManagement.Object,
            };
            var result = await controller.GetUploadUrl(parameter, default);

            // verify
            Mock.VerifyAll(fileManagement);
            fileManagement.VerifyNoOtherCalls();
            FileUpload resp = AssertHelper.AssertOKResult<FileUpload>(result);
            Assert.AreEqual(10, resp.expiration.Value);
            Assert.AreEqual("user/avatar.jpg", resp.filename);
        }
        #endregion
    }
}
