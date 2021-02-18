using Kaiyuanshe.OpenHackathon.Server.Auth;
using Kaiyuanshe.OpenHackathon.Server.Biz;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using Microsoft.Extensions.Primitives;
using Microsoft.Net.Http.Headers;
using Moq;
using NUnit.Framework;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Mime;
using System.Security.Claims;
using System.Text.Encodings.Web;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Auth
{
    [TestFixture]
    public class DefaultAuthHandlerTests
    {
        private readonly Mock<IOptionsMonitor<DefaultAuthSchemeOptions>> _options;
        private readonly Mock<ILoggerFactory> _loggerFactory;
        private readonly Mock<UrlEncoder> _encoder;
        private readonly Mock<ISystemClock> _clock;

        public DefaultAuthHandlerTests()
        {
            _options = new Mock<IOptionsMonitor<DefaultAuthSchemeOptions>>();
            _options.Setup(m => m.Get(It.IsAny<string>())).Returns(new DefaultAuthSchemeOptions());
            var logger = new Mock<ILogger<DefaultAuthHandler>>();
            _loggerFactory = new Mock<ILoggerFactory>();
            _loggerFactory.Setup(x => x.CreateLogger(It.IsAny<String>())).Returns(logger.Object);
            _encoder = new Mock<UrlEncoder>();
            _clock = new Mock<ISystemClock>();
        }

        [Test]
        public async Task AuthenticateAsyncTestTokenMissing()
        {
            // mock
            var userMgmtMock = new Mock<IUserManagement>();
            var httpContextMock = new Mock<HttpContext>();
            var httpRequestMock = new Mock<HttpRequest>();
            var headerMock = new Mock<IHeaderDictionary>();
            httpContextMock.SetupGet(h => h.Request).Returns(httpRequestMock.Object);
            httpRequestMock.SetupGet(h => h.Headers).Returns(headerMock.Object);
            headerMock.Setup(h => h.ContainsKey(HeaderNames.Authorization)).Returns(false);

            // test
            var handler = new DefaultAuthHandler(_options.Object, _loggerFactory.Object, _encoder.Object, _clock.Object, userMgmtMock.Object);
            await handler.InitializeAsync(new AuthenticationScheme(AuthConstant.AuthType.Token, AuthConstant.AuthType.Token, typeof(DefaultAuthHandler)), httpContextMock.Object);
            var result = await handler.AuthenticateAsync();

            // verify
            Mock.VerifyAll(userMgmtMock, httpContextMock, httpRequestMock, headerMock);
            Assert.IsFalse(result.Succeeded);
            Assert.IsTrue(result.Failure.Message.Contains("token is required"));
        }


        [TestCase("abc")]
        [TestCase("token")]
        [TestCase("")]
        public async Task AuthenticateAsyncTestTokenMalformatted(string tokenValue)
        {
            // mock
            var userMgmtMock = new Mock<IUserManagement>();
            var httpContextMock = new Mock<HttpContext>();
            var httpRequestMock = new Mock<HttpRequest>();
            var headerMock = new Mock<IHeaderDictionary>();
            httpContextMock.SetupGet(h => h.Request).Returns(httpRequestMock.Object);
            httpRequestMock.SetupGet(h => h.Headers).Returns(headerMock.Object);
            headerMock.Setup(h => h.ContainsKey(HeaderNames.Authorization)).Returns(true);
            headerMock.SetupGet(p => p[HeaderNames.Authorization]).Returns(new StringValues(tokenValue));

            // test
            var handler = new DefaultAuthHandler(_options.Object, _loggerFactory.Object, _encoder.Object, _clock.Object, userMgmtMock.Object);
            await handler.InitializeAsync(new AuthenticationScheme(AuthConstant.AuthType.Token, AuthConstant.AuthType.Token, typeof(DefaultAuthHandler)), httpContextMock.Object);
            var result = await handler.AuthenticateAsync();

            // verify
            Mock.VerifyAll(userMgmtMock, httpContextMock, httpRequestMock, headerMock);
            Assert.IsFalse(result.Succeeded);
            Assert.IsTrue(result.Failure.Message.Contains("token is required"));
        }

        [Test]
        public async Task AuthenticateAsyncTestPassed()
        {
            string token = "TOKENVALUE";
            CancellationToken cancellationToken = CancellationToken.None;
            IEnumerable<Claim> claims = new List<Claim>
            {
               new Claim("type", "value", "valueType", "issuer"),
            };

            // mock
            var userMgmtMock = new Mock<IUserManagement>();
            userMgmtMock.Setup(m => m.GetCurrentUserClaimsAsync(token, cancellationToken)).ReturnsAsync(claims);
            var httpContextMock = new Mock<HttpContext>();
            var httpRequestMock = new Mock<HttpRequest>();
            var headerMock = new Mock<IHeaderDictionary>();
            httpContextMock.SetupGet(h => h.Request).Returns(httpRequestMock.Object);
            httpRequestMock.SetupGet(h => h.Headers).Returns(headerMock.Object);
            headerMock.Setup(h => h.ContainsKey(HeaderNames.Authorization)).Returns(true);
            headerMock.SetupGet(p => p[HeaderNames.Authorization]).Returns(new StringValues("token TOKENVALUE"));

            // test
            var handler = new DefaultAuthHandler(_options.Object, _loggerFactory.Object, _encoder.Object, _clock.Object, userMgmtMock.Object);
            await handler.InitializeAsync(new AuthenticationScheme(AuthConstant.AuthType.Token, AuthConstant.AuthType.Token, typeof(DefaultAuthHandler)), httpContextMock.Object);
            var result = await handler.AuthenticateAsync();

            // verify
            Mock.VerifyAll(userMgmtMock, httpContextMock, httpRequestMock, headerMock);
            Assert.IsTrue(result.Succeeded);
            Assert.IsNotNull(result.Principal);
            Assert.AreEqual(1, result.Principal.Claims.Count());
            var claim = result.Principal.Claims.First();
            Assert.AreEqual("type", claim.Type);
            Assert.AreEqual("value", claim.Value);
            Assert.AreEqual("valueType", claim.ValueType);
            Assert.AreEqual("issuer", claim.Issuer);
        }

        [Test]
        public async Task HandleChallengeAsyncTest()
        {
            AuthenticationProperties authenticationProperties = new AuthenticationProperties();
            Func<HttpResponse, string, CancellationToken, Task> writeAsync = (resp, text, token) => Task.CompletedTask;

            // mock
            var userMgmtMock = new Mock<IUserManagement>();
            var httpContextMock = new Mock<HttpContext>();
            var httpResponseMock = new Mock<HttpResponse>();
            httpContextMock.SetupGet(h => h.Response).Returns(httpResponseMock.Object);
            httpResponseMock.SetupSet(m => m.StatusCode = 401);
            httpResponseMock.SetupSet(m => m.ContentType = MediaTypeNames.Application.Json);

            // test
            var handler = new DefaultAuthHandler(_options.Object, _loggerFactory.Object, _encoder.Object, _clock.Object, userMgmtMock.Object, writeAsync);
            await handler.InitializeAsync(new AuthenticationScheme(AuthConstant.AuthType.Token, AuthConstant.AuthType.Token, typeof(DefaultAuthHandler)), httpContextMock.Object);
            await handler.ChallengeAsync(authenticationProperties);

            // verify
            Mock.VerifyAll(userMgmtMock, httpContextMock, httpResponseMock);
            userMgmtMock.VerifyNoOtherCalls();
            httpContextMock.VerifyNoOtherCalls();
            httpResponseMock.VerifyNoOtherCalls();
        }
    }
}
