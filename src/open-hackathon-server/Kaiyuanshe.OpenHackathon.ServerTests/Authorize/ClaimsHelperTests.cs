using Kaiyuanshe.OpenHackathon.Server.Authorize;
using NUnit.Framework;
using System;
using System.Collections.Generic;
using System.Security.Claims;
using System.Text;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Authorize
{
    [TestFixture]
    public class ClaimsHelperTests
    {
        [Test]
        public void IsPlatformAdministratorTest()
        {
            Assert.IsFalse(ClaimsHelper.IsPlatformAdministrator(null));

            Assert.IsFalse(ClaimsHelper.IsPlatformAdministrator(new ClaimsPrincipal(
                new ClaimsIdentity())));

            Assert.IsFalse(ClaimsHelper.IsPlatformAdministrator(new ClaimsPrincipal(
                new ClaimsIdentity(new List<Claim> { }))));

            Assert.IsFalse(ClaimsHelper.IsPlatformAdministrator(new ClaimsPrincipal(
                new ClaimsIdentity(new List<Claim>
                {
                    new Claim("type", "value")
                }))));

            Assert.IsTrue(ClaimsHelper.IsPlatformAdministrator(new ClaimsPrincipal(
               new ClaimsIdentity(new List<Claim>
               {
                    new Claim("type", "value"),
                    new Claim(ClaimConstants.ClaimType.PlatformAdministrator, "foo")
               }))));

        }
    }
}
