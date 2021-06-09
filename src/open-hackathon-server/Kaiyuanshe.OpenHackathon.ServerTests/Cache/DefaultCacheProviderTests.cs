using Kaiyuanshe.OpenHackathon.Server.Cache;
using NUnit.Framework;
using System;
using System.Collections.Generic;
using System.Runtime.Caching;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Cache
{
    public class DefaultCacheProviderTests
    {
        [Test]
        public async Task GetOrAddAsync()
        {
            CacheEntry<string> entry = new CacheEntry<string>(
                CacheEntryType.Default,
                "key",
                false,
                new CacheItemPolicy { AbsoluteExpiration = DateTime.Now.AddDays(1) },
                (token) => { return Task.FromResult("second"); }
                );
            CancellationToken cancellationToken = CancellationToken.None;

            MemoryCache.Default.Add(entry.CacheKey, "first", entry.CachePolicy);
            var cacheProvider = new DefaultCacheProvider();
            string value = await cacheProvider.GetOrAddAsync(entry, cancellationToken);
            Assert.AreEqual("second", value);
        }

        [Test]
        public async Task RefreshAllAsync()
        {
            // not autofresh
            CacheEntry<string> first = new CacheEntry<string>(
                CacheEntryType.Default,
                "first",
                false,
                new CacheItemPolicy { AbsoluteExpiration = DateTime.Now.AddDays(1) },
                (token) => { return Task.FromResult("first"); }
                );
            // existing in cache
            CacheEntry<string> second = new CacheEntry<string>(
                CacheEntryType.Default,
                "second",
                true,
                new CacheItemPolicy { AbsoluteExpiration = DateTime.Now.AddDays(1) },
                (token) => { return Task.FromResult("second"); }
                );
            // refreshed
            CacheEntry<string> third = new CacheEntry<string>(
                CacheEntryType.Default,
                "third",
                true,
                new CacheItemPolicy { AbsoluteExpiration = DateTime.Now.AddDays(1) },
                (token) => { return Task.FromResult("third"); }
                );
            CancellationToken cancellationToken = CancellationToken.None;

            var cacheProvider = new DefaultCacheProvider();
            await cacheProvider.GetOrAddAsync(first, cancellationToken);
            await cacheProvider.GetOrAddAsync(second, cancellationToken);
            await cacheProvider.GetOrAddAsync(third, cancellationToken);
            Assert.IsFalse(MemoryCache.Default.Contains(first.CacheKey));
            Assert.IsFalse(MemoryCache.Default.Contains(second.CacheKey));
            Assert.IsFalse(MemoryCache.Default.Contains(third.CacheKey));

            MemoryCache.Default.Add(second.CacheKey, "second-value", second.CachePolicy);
            await cacheProvider.RefreshAllAsync(cancellationToken);

            Assert.IsFalse(MemoryCache.Default.Contains(first.CacheKey));
            Assert.IsTrue(MemoryCache.Default.Contains(second.CacheKey));
            Assert.AreEqual("second-value", (string)MemoryCache.Default.Get(second.CacheKey));
            Assert.IsTrue(MemoryCache.Default.Contains(third.CacheKey));
            Assert.AreEqual("third", (string)MemoryCache.Default.Get(third.CacheKey));
        }

        [Test]
        public async Task RefreshAsync()
        {
            CacheEntry<string> entry = new CacheEntry<string>(
                CacheEntryType.User,
                "t3",
                false,
                new CacheItemPolicy { AbsoluteExpiration = DateTime.Now.AddDays(1) },
                (token) => { return Task.FromResult("t3"); }
                );
            CancellationToken cancellationToken = CancellationToken.None;

            var cacheProvider = new DefaultCacheProvider();
            await cacheProvider.GetOrAddAsync(entry, cancellationToken);
            Assert.IsFalse(MemoryCache.Default.Contains(entry.CacheKey));

            await cacheProvider.RefreshAsync(entry.CacheEntryType, entry.SubCacheKey, cancellationToken);
            Assert.IsTrue(MemoryCache.Default.Contains(entry.CacheKey));
            Assert.AreEqual("t3", (string)MemoryCache.Default.Get(entry.CacheKey));

            await cacheProvider.RefreshAsync(entry.CacheEntryType, "unknown", cancellationToken);
            Assert.IsFalse(MemoryCache.Default.Contains(CacheEntry.GetCacheKey(entry.CacheEntryType, "unknown")));
        }

        [Test]
        public async Task GetOrAddInternalTest()
        {
            CacheEntry<string> entry = new CacheEntry<string>(
               CacheEntryType.Token,
               "internal",
               false,
               new CacheItemPolicy { AbsoluteExpiration = DateTime.Now.AddDays(1) },
               (token) =>
               {
                   return Task.FromResult("first");
               });
            CancellationToken cancellationToken = CancellationToken.None;

            var cacheProvider = new DefaultCacheProvider();

            MemoryCache.Default.Add(entry.CacheKey, "existing", entry.CachePolicy);
            string value = (string)await cacheProvider.GetOrAddAsyncInternal(entry, cancellationToken);
            Assert.AreEqual("existing", value);

            MemoryCache.Default.Remove(entry.CacheKey);
            value = (string)await cacheProvider.GetOrAddAsyncInternal(entry, cancellationToken);
            Assert.AreEqual("first", value);
        }
    }
}
