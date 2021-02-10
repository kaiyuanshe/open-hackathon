using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Abstractions;
using Microsoft.AspNetCore.Mvc.Filters;
using Microsoft.AspNetCore.Routing;
using Microsoft.Extensions.Primitives;
using Microsoft.Net.Http.Headers;
using Moq;
using NUnit.Framework;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Threading;
using static Kaiyuanshe.OpenHackathon.Server.Filters.TokenRequiredAttribute;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Filters
{
    [TestFixture]
    public class TokenRequiredFilterTests
    {
        [Test]
        public void OnActionExecutingTestMissing()
        {
            // setup
            var loginManagerMock = new Mock<IUserManagement>();
            var httpContextMock = new Mock<HttpContext>();
            var httpRequestMock = new Mock<HttpRequest>();
            var headerMock = new Mock<IHeaderDictionary>();
            var filterMetadataMock = new Mock<IList<IFilterMetadata>>();
            httpContextMock.SetupGet(h => h.Request).Returns(httpRequestMock.Object).Verifiable();
            httpRequestMock.SetupGet(h => h.Headers).Returns(headerMock.Object).Verifiable();
            headerMock.Setup(h => h.ContainsKey(HeaderNames.Authorization)).Returns(false).Verifiable();

            var actionContext = new ActionContext(httpContextMock.Object, new RouteData(), new ActionDescriptor());
            var context = new ActionExecutingContext(actionContext, filterMetadataMock.Object, new Dictionary<string, object>(), null);

            // test
            var filter = new TokenRequiredFilter(loginManagerMock.Object);
            filter.OnActionExecuting(context);

            Mock.VerifyAll(loginManagerMock, httpContextMock, httpRequestMock, headerMock);
            Assert.IsNotNull(context.Result);
            Assert.IsTrue(context.Result is ObjectResult);
            ObjectResult result = (ObjectResult)context.Result;
            Assert.AreEqual(401, result.StatusCode.GetValueOrDefault(0));
            Assert.IsTrue(result.Value is ErrorResponse);
            ErrorResponse error = (ErrorResponse)result.Value;
            Assert.AreEqual("Unauthorized", error.error.code);
            Assert.IsTrue(error.error.message.Contains("missing"));
        }

        [TestCase("abc")]
        [TestCase("token")]
        [TestCase("")]
        public void OnActionExecutingTestMalformat(string tokenValue)
        {
            // setup
            var loginManagerMock = new Mock<IUserManagement>();
            var httpContextMock = new Mock<HttpContext>();
            var httpRequestMock = new Mock<HttpRequest>();
            var headerMock = new Mock<IHeaderDictionary>();
            var filterMetadataMock = new Mock<IList<IFilterMetadata>>();
            httpContextMock.SetupGet(h => h.Request).Returns(httpRequestMock.Object).Verifiable();
            httpRequestMock.SetupGet(h => h.Headers).Returns(headerMock.Object).Verifiable();
            headerMock.Setup(h => h.ContainsKey(HeaderNames.Authorization)).Returns(true).Verifiable();
            headerMock.SetupGet(p => p[HeaderNames.Authorization]).Returns(new StringValues(tokenValue));

            var actionContext = new ActionContext(httpContextMock.Object, new RouteData(), new ActionDescriptor());
            var context = new ActionExecutingContext(actionContext, filterMetadataMock.Object, new Dictionary<string, object>(), null);

            // test
            var filter = new TokenRequiredFilter(loginManagerMock.Object);
            filter.OnActionExecuting(context);

            Mock.VerifyAll(loginManagerMock, httpContextMock, httpRequestMock, headerMock);
            Assert.IsNotNull(context.Result);
            Assert.IsTrue(context.Result is ObjectResult);
            ObjectResult result = (ObjectResult)context.Result;
            Assert.AreEqual(401, result.StatusCode.GetValueOrDefault(0));
            Assert.IsTrue(result.Value is ErrorResponse);
            ErrorResponse error = (ErrorResponse)result.Value;
            Assert.AreEqual("Unauthorized", error.error.code);
            Assert.IsTrue(error.error.message.Contains("malformatted"));
        }

        [Test]
        public void OnActionExecutingTestValidateFailed()
        {
            // setup
            var loginManagerMock = new Mock<IUserManagement>();
            loginManagerMock.Setup(p => p.ValidateTokenAsync("TOKEN", It.IsAny<CancellationToken>())).ReturnsAsync(new ValidationResult("whatever")).Verifiable();
            var httpContextMock = new Mock<HttpContext>();
            var httpRequestMock = new Mock<HttpRequest>();
            var headerMock = new Mock<IHeaderDictionary>();
            var filterMetadataMock = new Mock<IList<IFilterMetadata>>();
            httpContextMock.SetupGet(h => h.Request).Returns(httpRequestMock.Object).Verifiable();
            httpRequestMock.SetupGet(h => h.Headers).Returns(headerMock.Object).Verifiable();
            headerMock.Setup(h => h.ContainsKey(HeaderNames.Authorization)).Returns(true).Verifiable();
            headerMock.SetupGet(p => p[HeaderNames.Authorization]).Returns(new StringValues("token TOKEN"));

            var actionContext = new ActionContext(httpContextMock.Object, new RouteData(), new ActionDescriptor());
            var context = new ActionExecutingContext(actionContext, filterMetadataMock.Object, new Dictionary<string, object>(), null);

            // test
            var filter = new TokenRequiredFilter(loginManagerMock.Object);
            filter.OnActionExecuting(context);

            Mock.VerifyAll(loginManagerMock, httpContextMock, httpRequestMock, headerMock);
            Assert.IsNotNull(context.Result);
            Assert.IsTrue(context.Result is ObjectResult);
            ObjectResult result = (ObjectResult)context.Result;
            Assert.AreEqual(401, result.StatusCode.GetValueOrDefault(0));
            Assert.IsTrue(result.Value is ErrorResponse);
            ErrorResponse error = (ErrorResponse)result.Value;
            Assert.AreEqual("Unauthorized", error.error.code);
            Assert.IsTrue(error.error.message.Contains("whatever"));
        }

        [Test]
        public void OnActionExecutingTestPassed()
        {
            // setup
            var loginManagerMock = new Mock<IUserManagement>();
            loginManagerMock.Setup(p => p.ValidateTokenAsync("TOKEN", It.IsAny<CancellationToken>())).ReturnsAsync(ValidationResult.Success).Verifiable();
            var httpContextMock = new Mock<HttpContext>();
            var httpRequestMock = new Mock<HttpRequest>();
            var headerMock = new Mock<IHeaderDictionary>();
            var filterMetadataMock = new Mock<IList<IFilterMetadata>>();
            httpContextMock.SetupGet(h => h.Request).Returns(httpRequestMock.Object).Verifiable();
            httpRequestMock.SetupGet(h => h.Headers).Returns(headerMock.Object).Verifiable();
            headerMock.Setup(h => h.ContainsKey(HeaderNames.Authorization)).Returns(true).Verifiable();
            headerMock.SetupGet(p => p[HeaderNames.Authorization]).Returns(new StringValues("token TOKEN"));

            var actionContext = new ActionContext(httpContextMock.Object, new RouteData(), new ActionDescriptor());
            var context = new ActionExecutingContext(actionContext, filterMetadataMock.Object, new Dictionary<string, object>(), null);

            // test
            var filter = new TokenRequiredFilter(loginManagerMock.Object);
            filter.OnActionExecuting(context);

            Mock.VerifyAll(loginManagerMock, httpContextMock, httpRequestMock, headerMock);
            Assert.IsNull(context.Result);
        }
    }
}
