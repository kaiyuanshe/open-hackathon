using Authing.ApiClient.Types;
using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Controllers;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.ResponseBuilder;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.AspNetCore.Mvc;
using Moq;
using NUnit.Framework;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Controllers
{
    [TestFixture]
    public class LoginControllerTests
    {
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
            var controller = new LoginController
            {
                userManagement = loginManagerMoq.Object,
            };
            var resp = await controller.Authing(parameter, cancellationToken);

            // Verify
            Mock.VerifyAll();
            loginManagerMoq.Verify(p => p.ValidateTokenRemotelyAsync("pool", "token", cancellationToken), Times.Once);
            loginManagerMoq.VerifyNoOtherCalls();

            Assert.IsTrue(resp is BadRequestObjectResult);
            Assert.IsTrue(((BadRequestObjectResult)resp).Value is ErrorResponse);
            var errorResponse = ((BadRequestObjectResult)resp).Value as ErrorResponse;
            Assert.AreEqual("BadArgument", errorResponse.error.code);
            Assert.IsTrue(errorResponse.error.message.Contains("400"));
            Assert.IsTrue(errorResponse.error.message.Contains("Some Message"));
        }
    }
}
