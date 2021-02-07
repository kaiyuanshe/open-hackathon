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
        public async Task AuthingTest()
        {
            // input
            var parameter = new UserLoginInfo { Token = "token" };
            var cancellationToken = CancellationToken.None;
            var userEntity = new UserEntity { Company = "contoso" };
            var tokenEntity = new UserTokenEntity { Token = "token2" };

            // Moq
            var loginManagerMoq = new Mock<ILoginManager>();
            loginManagerMoq.Setup(p => p.AuthingAsync(parameter, cancellationToken)).ReturnsAsync(userEntity);
            loginManagerMoq.Setup(p => p.GetTokenEntityAsync("token", cancellationToken)).ReturnsAsync(tokenEntity);

            // test
            var controller = new LoginController
            {
                LoginManager = loginManagerMoq.Object,
                ResponseBuilder = new DefaultResponseBuilder(),
            };
            var resp = await controller.Authing(parameter, cancellationToken);

            // Verify
            Mock.VerifyAll();
            loginManagerMoq.Verify(p => p.AuthingAsync(parameter, cancellationToken), Times.Once);
            loginManagerMoq.Verify(p => p.GetTokenEntityAsync("token", cancellationToken), Times.Once);
            loginManagerMoq.VerifyNoOtherCalls();
            Assert.IsTrue(resp is OkObjectResult);
            Assert.IsTrue(((OkObjectResult)resp).Value is UserLoginInfo);
            var info = ((OkObjectResult)resp).Value as UserLoginInfo;
            Assert.AreEqual(null, info.UserName);
            Assert.AreEqual("contoso", info.Company);
            Assert.AreEqual("token2", info.Token);
        }
    }
}
