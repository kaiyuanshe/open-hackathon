using Kaiyuanshe.OpenHackathon.Server;
using NUnit.Framework;
using System;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Helpers
{
    [TestFixture]
    public class EnvHelperTests
    {
        [Test]
        public void IsDevelopmentTestTrue()
        {
            Environment.SetEnvironmentVariable("ASPNETCORE_ENVIRONMENT", "Development", EnvironmentVariableTarget.Process);
            Assert.IsTrue(EnvHelper.IsDevelopment());
        }

        [Test]
        public void IsRunningInTestsTest()
        {
            Assert.IsTrue(EnvHelper.IsRunningInTests());
        }
    }
}
