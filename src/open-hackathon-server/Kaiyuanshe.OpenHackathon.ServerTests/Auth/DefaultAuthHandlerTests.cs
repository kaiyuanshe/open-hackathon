using Kaiyuanshe.OpenHackathon.Server;
using Kaiyuanshe.OpenHackathon.Server.Auth;
using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Cache;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc.Infrastructure;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using Microsoft.Extensions.Primitives;
using Microsoft.Net.Http.Headers;
using Moq;
using NUnit.Framework;
using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
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
        public async Task AuthenticateAsyncTest_TokenMissing()
        {
            // mock
            var userManagement = new Mock<IUserManagement>();
            var httpContext = new Mock<HttpContext>();
            var httpRequest = new Mock<HttpRequest>();
            var httpHeaders = new Mock<IHeaderDictionary>();
            httpContext.SetupGet(h => h.Request).Returns(httpRequest.Object);
            httpRequest.SetupGet(h => h.Headers).Returns(httpHeaders.Object);
            httpHeaders.Setup(h => h.ContainsKey(HeaderNames.Authorization)).Returns(false);
            var factory = new Mock<ProblemDetailsFactory>();
            var cache = new Mock<ICacheProvider>();

            // test
            var handler = new DefaultAuthHandler(_options.Object, _loggerFactory.Object, _encoder.Object, _clock.Object, userManagement.Object, cache.Object, factory.Object);
            await handler.InitializeAsync(new AuthenticationScheme(AuthConstant.AuthType.Token, AuthConstant.AuthType.Token, typeof(DefaultAuthHandler)), httpContext.Object);
            var result = await handler.AuthenticateAsync();

            // verify
            Mock.VerifyAll(userManagement, httpContext, httpRequest, httpHeaders, cache);
            Assert.IsFalse(result.Succeeded);
            Assert.AreEqual(Resources.Auth_Unauthorized, result.Failure.Message);
        }


        [TestCase("abc")]
        [TestCase("token")]
        [TestCase("")]
        public async Task AuthenticateAsyncTest_TokenMalformatted(string tokenValue)
        {
            // mock
            var userManagement = new Mock<IUserManagement>();
            var httpContext = new Mock<HttpContext>();
            var httpRequest = new Mock<HttpRequest>();
            var httpHeaders = new Mock<IHeaderDictionary>();
            httpContext.SetupGet(h => h.Request).Returns(httpRequest.Object);
            httpRequest.SetupGet(h => h.Headers).Returns(httpHeaders.Object);
            httpHeaders.Setup(h => h.ContainsKey(HeaderNames.Authorization)).Returns(true);
            httpHeaders.SetupGet(p => p[HeaderNames.Authorization]).Returns(new StringValues(tokenValue));
            var factory = new Mock<ProblemDetailsFactory>();
            var cache = new Mock<ICacheProvider>();

            // test
            var handler = new DefaultAuthHandler(_options.Object, _loggerFactory.Object, _encoder.Object, _clock.Object, userManagement.Object, cache.Object, factory.Object);
            await handler.InitializeAsync(new AuthenticationScheme(AuthConstant.AuthType.Token, AuthConstant.AuthType.Token, typeof(DefaultAuthHandler)), httpContext.Object);
            var result = await handler.AuthenticateAsync();

            // verify
            Mock.VerifyAll(userManagement, httpContext, httpRequest, httpHeaders, cache);
            Assert.IsFalse(result.Succeeded);
            Assert.AreEqual(Resources.Auth_Unauthorized, result.Failure.Message);
        }

        [Test]
        public async Task AuthenticateAsyncTest_ValidateFailed()
        {
            string token = "TOKENVALUE";
            ValidationResult validationResult = new ValidationResult("reason");

            // mock
            var userManagement = new Mock<IUserManagement>();
            userManagement.Setup(m => m.ValidateTokenAsync(token, It.IsAny<CancellationToken>())).ReturnsAsync(validationResult);
            var httpContext = new Mock<HttpContext>();
            var httpRequest = new Mock<HttpRequest>();
            var httpHeaders = new Mock<IHeaderDictionary>();
            httpContext.SetupGet(h => h.Request).Returns(httpRequest.Object);
            httpRequest.SetupGet(h => h.Headers).Returns(httpHeaders.Object);
            httpHeaders.Setup(h => h.ContainsKey(HeaderNames.Authorization)).Returns(true);
            httpHeaders.SetupGet(p => p[HeaderNames.Authorization]).Returns(new StringValues("token TOKENVALUE"));
            var factory = new Mock<ProblemDetailsFactory>();
            var cache = new Mock<ICacheProvider>();

            // test
            var handler = new DefaultAuthHandler(_options.Object, _loggerFactory.Object, _encoder.Object, _clock.Object, userManagement.Object, cache.Object, factory.Object);
            await handler.InitializeAsync(new AuthenticationScheme(AuthConstant.AuthType.Token, AuthConstant.AuthType.Token, typeof(DefaultAuthHandler)), httpContext.Object);
            var result = await handler.AuthenticateAsync();

            // verify
            Mock.VerifyAll(userManagement, httpContext, httpRequest, httpHeaders, cache);
            userManagement.VerifyNoOtherCalls();
            Assert.IsFalse(result.Succeeded);
            Assert.AreEqual(Resources.Auth_Unauthorized, result.Failure.Message);
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
            ValidationResult validationResult = ValidationResult.Success;

            // mock
            var userManagement = new Mock<IUserManagement>();
            userManagement.Setup(m => m.ValidateTokenAsync(token, It.IsAny<CancellationToken>())).ReturnsAsync(validationResult);
            var httpContext = new Mock<HttpContext>();
            var httpRequest = new Mock<HttpRequest>();
            var httpHeaders = new Mock<IHeaderDictionary>();
            httpContext.SetupGet(h => h.Request).Returns(httpRequest.Object);
            httpRequest.SetupGet(h => h.Headers).Returns(httpHeaders.Object);
            httpHeaders.Setup(h => h.ContainsKey(HeaderNames.Authorization)).Returns(true);
            httpHeaders.SetupGet(p => p[HeaderNames.Authorization]).Returns(new StringValues("token TOKENVALUE"));
            var factory = new Mock<ProblemDetailsFactory>();
            var cache = new Mock<ICacheProvider>();
            cache.Setup(m => m.GetOrAddAsync(It.IsAny<CacheEntry<IEnumerable<Claim>>>(), It.IsAny<CancellationToken>())).ReturnsAsync(claims);

            // test
            var handler = new DefaultAuthHandler(_options.Object, _loggerFactory.Object, _encoder.Object, _clock.Object, userManagement.Object, cache.Object, factory.Object);
            await handler.InitializeAsync(new AuthenticationScheme(AuthConstant.AuthType.Token, AuthConstant.AuthType.Token, typeof(DefaultAuthHandler)), httpContext.Object);
            var result = await handler.AuthenticateAsync();

            // verify
            Mock.VerifyAll(userManagement, httpContext, httpRequest, httpHeaders, cache);
            userManagement.VerifyNoOtherCalls();
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
            var userManagement = new Mock<IUserManagement>();
            var httpContext = new Mock<HttpContext>();
            var httpResponse = new Mock<HttpResponse>();
            httpContext.SetupGet(h => h.Response).Returns(httpResponse.Object);
            httpResponse.SetupSet(m => m.StatusCode = 401);
            httpResponse.SetupSet(m => m.ContentType = MediaTypeNames.Application.Json);
            var factory = new Mock<ProblemDetailsFactory>();
            var cache = new Mock<ICacheProvider>();

            // test
            var handler = new DefaultAuthHandler(_options.Object, _loggerFactory.Object, _encoder.Object, _clock.Object, userManagement.Object, cache.Object, factory.Object, writeAsync);
            await handler.InitializeAsync(new AuthenticationScheme(AuthConstant.AuthType.Token, AuthConstant.AuthType.Token, typeof(DefaultAuthHandler)), httpContext.Object);
            await handler.ChallengeAsync(authenticationProperties);

            // verify
            Mock.VerifyAll(userManagement, httpContext, httpResponse, cache);
            userManagement.VerifyNoOtherCalls();
            httpContext.VerifyNoOtherCalls();
            httpResponse.VerifyNoOtherCalls();
        }
    }
}
