using Kaiyuanshe.OpenHackathon.Server.Auth;
using Microsoft.AspNetCore.Authorization;
using NUnit.Framework;
using System.Collections.Generic;
using System.Security.Claims;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Auth
{
    [TestFixture]
    public class PlatformAdministratorHandlerTest
    {
        [Test]
        public async Task HandleAsyncTest_IsPlatformAdmin()
        {
            // data
            var requirements = new List<IAuthorizationRequirement>
            {
                new PlatformAdministratorRequirement(),
            };
            var claims = new List<Claim>
            {
                ClaimsHelper.PlatformAdministrator("userid"),
            };
            var claimsPrincipal = new ClaimsPrincipal(new ClaimsIdentity(claims));
            var context = new AuthorizationHandlerContext(requirements, claimsPrincipal, null);

            // test
            var handler = new PlatformAdministratorHandler();
            await handler.HandleAsync(context);

            Assert.IsTrue(context.HasSucceeded);
        }

        [Test]
        public async Task HandleAsyncTest_IsNotPlatformAdmin()
        {
            // data
            var requirements = new List<IAuthorizationRequirement>
            {
                new PlatformAdministratorRequirement(),
            };
            var claims = new List<Claim>();
            var claimsPrincipal = new ClaimsPrincipal(new ClaimsIdentity(claims));
            var context = new AuthorizationHandlerContext(requirements, claimsPrincipal, null);

            // test
            var handler = new PlatformAdministratorHandler();
            await handler.HandleAsync(context);

            Assert.IsFalse(context.HasSucceeded);
        }
    }
}
