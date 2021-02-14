using Kaiyuanshe.OpenHackathon.Server.Biz;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Abstractions;
using Microsoft.AspNetCore.Mvc.Filters;
using Microsoft.AspNetCore.Routing;
using Microsoft.Extensions.Primitives;
using Microsoft.Net.Http.Headers;
using Moq;
using NUnit.Framework;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Claims;
using System.Text;
using System.Threading;
using static Kaiyuanshe.OpenHackathon.Server.Filters.HackathonClaimsAttribute;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Filters
{
    [TestFixture]
    public class HackathonClaimsAttributeTests
    {
        [Test]
        public void OnActionExecutingTestNoAuthHeader()
        {
            // setup
            var userMgmtMock = new Mock<IUserManagement>();
            var httpContextMock = new Mock<HttpContext>();
            var httpRequestMock = new Mock<HttpRequest>();
            var headerMock = new Mock<IHeaderDictionary>();
            var filterMetadataMock = new Mock<IList<IFilterMetadata>>();
            httpContextMock.SetupGet(h => h.Request).Returns(httpRequestMock.Object);
            httpRequestMock.SetupGet(h => h.Headers).Returns(headerMock.Object);
            headerMock.Setup(h => h.ContainsKey(HeaderNames.Authorization)).Returns(false);

            var actionContext = new ActionContext(httpContextMock.Object, new RouteData(), new ActionDescriptor());
            var context = new ActionExecutingContext(actionContext, filterMetadataMock.Object, new Dictionary<string, object>(), null);

            // test
            var filter = new HackathonClaimsFilter(userMgmtMock.Object);
            filter.OnActionExecuting(context);

            // verify
            Mock.VerifyAll(userMgmtMock, httpContextMock, httpRequestMock, headerMock);
            Assert.IsNull(context.HttpContext.User);
        }

        [TestCase("abc")]
        [TestCase("token")]
        [TestCase("")]
        public void OnActionExecutingTestMalformat(string tokenValue)
        {
            // setup
            var userMgmtMock = new Mock<IUserManagement>();
            var httpContextMock = new Mock<HttpContext>();
            var httpRequestMock = new Mock<HttpRequest>();
            var headerMock = new Mock<IHeaderDictionary>();
            var filterMetadataMock = new Mock<IList<IFilterMetadata>>();
            httpContextMock.SetupGet(h => h.Request).Returns(httpRequestMock.Object);
            httpRequestMock.SetupGet(h => h.Headers).Returns(headerMock.Object);
            headerMock.Setup(h => h.ContainsKey(HeaderNames.Authorization)).Returns(true);
            headerMock.SetupGet(p => p[HeaderNames.Authorization]).Returns(new StringValues(tokenValue));

            var actionContext = new ActionContext(httpContextMock.Object, new RouteData(), new ActionDescriptor());
            var context = new ActionExecutingContext(actionContext, filterMetadataMock.Object, new Dictionary<string, object>(), null);

            // test
            var filter = new HackathonClaimsFilter(userMgmtMock.Object);
            filter.OnActionExecuting(context);

            // verify
            Mock.VerifyAll(userMgmtMock, httpContextMock, httpRequestMock, headerMock);
            Assert.IsNull(context.HttpContext.User);
        }

        [Test]
        public void OnActionExecutingTestPassed()
        {
            string token = "TOKENVALUE";
            CancellationToken cancellationToken = CancellationToken.None;
            IEnumerable<Claim> claims = new List<Claim>
            {
               new Claim("type", "value", "valueType", "issuer"),
            };

            // setup
            var userMgmtMock = new Mock<IUserManagement>();
            userMgmtMock.Setup(m => m.GetCurrentUserClaimsAsync(token, cancellationToken)).ReturnsAsync(claims);
            var httpContextMock = new Mock<HttpContext>();
            httpContextMock.SetupSet((c) => c.User = It.IsAny<ClaimsPrincipal>());
            var httpRequestMock = new Mock<HttpRequest>();
            var headerMock = new Mock<IHeaderDictionary>();
            var filterMetadataMock = new Mock<IList<IFilterMetadata>>();
            httpContextMock.SetupGet(h => h.Request).Returns(httpRequestMock.Object);
            httpRequestMock.SetupGet(h => h.Headers).Returns(headerMock.Object);
            headerMock.Setup(h => h.ContainsKey(HeaderNames.Authorization)).Returns(true);
            headerMock.SetupGet(p => p[HeaderNames.Authorization]).Returns(new StringValues("token TOKENVALUE"));

            var actionContext = new ActionContext(httpContextMock.Object, new RouteData(), new ActionDescriptor());
            var context = new ActionExecutingContext(actionContext, filterMetadataMock.Object, new Dictionary<string, object>(), null);

            // test
            var filter = new HackathonClaimsFilter(userMgmtMock.Object);
            filter.OnActionExecuting(context);

            // verify
            Mock.VerifyAll(userMgmtMock, httpContextMock, httpRequestMock, headerMock);
        }
    }
}
