using Authing.ApiClient.Types;
using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Controllers;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.ResponseBuilder;
using Moq;
using NUnit.Framework;
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
            var parameter = new FileUpload { expiration = 10, filename = "user/avatar.jpg" };
            string url = "https://container.blob.core.chinacloudapi.cn/kysuser/user/avatar.jpg?sv=2018-03-28&sr=b&sig=JT1H%2FcjWK1xbwK3gy1qXXbXAxuQBTmYoCwpmK2Z9Ls0%3D&st=2021-07-04T09%3A25%3A39Z&se=2021-07-04T09%3A32%3A39Z&sp=rw";

            // mock
            var userManagement = new Mock<IUserManagement>();
            userManagement.Setup(u => u.GetUploadUrl(parameter.expiration.GetValueOrDefault(), parameter.filename)).Returns(url);

            // test
            var controller = new UserController
            {
                UserManagement = userManagement.Object,
            };
            var result = await controller.GetUploadUrl(parameter);

            // verify
            Mock.VerifyAll(userManagement);
            userManagement.VerifyNoOtherCalls();
            var resp = AssertHelper.AssertOKResult<string>(result);
            Assert.AreEqual(resp, url);
        }
        #endregion
    }
}
