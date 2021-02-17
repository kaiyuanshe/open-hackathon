using Kaiyuanshe.OpenHackathon.Server;
using NUnit.Framework;
using System;
using System.Collections.Generic;
using System.Runtime.Caching;
using System.Text;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Helpers
{
    [TestFixture]
    public class CacheHelperTests
    {
        [Test]
        public void GetOrAddTest()
        {
            string key = "key";
            string value = CacheHelper.GetOrAdd(key, () => "first",
                new CacheItemPolicy
                {
                    AbsoluteExpiration = DateTime.Now.AddDays(1)
                });
            Assert.AreEqual("first", value);

            value = CacheHelper.GetOrAdd(key, () => "second",
                new CacheItemPolicy
                {
                    AbsoluteExpiration = DateTime.Now.AddDays(1)
                });
            Assert.AreEqual("second", value);
        }

        [Test]
        public async Task GetOrAddAsyncTest()
        {
            string key = "key";
            string value = await CacheHelper.GetOrAddAsync(key, () => Task.FromResult("first"),
                new CacheItemPolicy
                {
                    AbsoluteExpiration = DateTime.Now.AddDays(1)
                });
            Assert.AreEqual("first", value);

            value = await CacheHelper.GetOrAddAsync(key, () => Task.FromResult("second"),
                new CacheItemPolicy
                {
                    AbsoluteExpiration = DateTime.Now.AddDays(1)
                });
            Assert.AreEqual("second", value);
        }

        [Test]
        public async Task GetOrAddInternalTest()
        {
            string key = "key";
            string value = await CacheHelper.GetOrAddInternal(key, () => Task.FromResult("first"),
                new CacheItemPolicy
                {
                    AbsoluteExpiration = DateTime.Now.AddDays(1)
                });
            Assert.AreEqual("first", value);

            value = await CacheHelper.GetOrAddInternal(key, () => Task.FromResult("second"),
                new CacheItemPolicy
                {
                    AbsoluteExpiration = DateTime.Now.AddDays(1)
                });
            Assert.AreEqual("first", value);
        }
    }
}
