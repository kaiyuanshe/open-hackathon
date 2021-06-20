using Microsoft.Extensions.Logging;
using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.Caching;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Cache
{
    public interface ICacheProvider
    {
        /// <summary>
        /// Get or add cached value
        /// </summary>
        /// <typeparam name="TValue"></typeparam>
        /// <param name="cacheEntry"></param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        public Task<TValue> GetOrAddAsync<TValue>(CacheEntry<TValue> cacheEntry, CancellationToken cancellationToken);

        /// <summary>
        /// Removes a cache entry from the cache.
        /// </summary>
        /// <param name="key"></param>
        /// <returns>If the entry is found in the cache, the removed cache entry; otherwise, null.</returns>
        public object Remove(string key);

        /// <summary>
        /// Refresh the cached value. Ignored if CacheEntry is not found.
        /// </summary>
        /// <param name="cacheKey"></param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        public Task RefreshAsync(string cacheKey, CancellationToken cancellationToken);

        /// <summary>
        /// Refresh all cached values if expired and AutoRefresh is enabled
        /// </summary>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        public Task RefreshAllAsync(CancellationToken cancellationToken);
    }

    public class DefaultCacheProvider : ICacheProvider
    {
        static MemoryCache cache = MemoryCache.Default;
        static Dictionary<string, CacheEntry> cacheEntries = new Dictionary<string, CacheEntry>();
        private readonly ILogger Logger;

        public DefaultCacheProvider(ILogger<DefaultCacheProvider> logger)
        {
            Logger = logger;
        }

        public async Task<TValue> GetOrAddAsync<TValue>(CacheEntry<TValue> cacheEntry, CancellationToken cancellationToken)
        {
            cacheEntries[cacheEntry.CacheKey] = cacheEntry;

            // disable cache in Dev or Unit Tests
            if (EnvHelper.IsDevelopment() || EnvHelper.IsRunningInTests())
            {
                return (TValue)await cacheEntry.SupplyValueAsync(cancellationToken);
            }

            return (TValue)await GetOrAddAsyncInternal(cacheEntry, cancellationToken);
        }

        public async Task RefreshAllAsync(CancellationToken cancellationToken)
        {
            foreach (var cacheEntry in cacheEntries.Values)
            {
                if (!cacheEntry.AutoRefresh)
                {
                    continue;
                }

                if (cache.Contains(cacheEntry.CacheKey))
                {
                    continue;
                }

                Logger?.LogInformation($"Refreshing entry in cache: {cacheEntry.CacheKey}");
                var value = await cacheEntry.SupplyValueAsync(cancellationToken);
                cache.Add(cacheEntry.CacheKey, value, cacheEntry.CachePolicy);
            }
        }

        public async Task RefreshAsync(string cacheKey, CancellationToken cancellationToken)
        {
            if (cacheEntries.TryGetValue(cacheKey, out CacheEntry cacheEntry))
            {
                var value = await cacheEntry.SupplyValueAsync(cancellationToken);
                cache.Add(cacheEntry.CacheKey, value, cacheEntry.CachePolicy);
            }
        }

        public object Remove(string key)
        {
            if (cache.Contains(key))
            {
                return cache.Remove(key);
            }

            return null;
        }

        internal async Task<object> GetOrAddAsyncInternal(CacheEntry cacheEntry, CancellationToken cancellationToken)
        {
            if (!cache.Contains(cacheEntry.CacheKey))
            {
                var value = await cacheEntry.SupplyValueAsync(cancellationToken);
                if (value != null)
                {
                    cache.Add(cacheEntry.CacheKey, value, cacheEntry.CachePolicy);
                    return value;
                }
                else
                {
                    return default;
                }
            }
            else
            {
                return cache[cacheEntry.CacheKey];
            }
        }
    }

    public static class CacheProviderExtension
    {
        public static Task<TValue> GetOrAddAsync<TValue>(
            this ICacheProvider cache,
            string cacheKey,
            TimeSpan slidingExpiration,
            Func<CancellationToken, Task<TValue>> supplyVaule,
            bool autoRefresh = false,
            CancellationToken cancellationToken = default)
        {
            if (cache == null)
                return null;

            var entry = new CacheEntry<TValue>(cacheKey, slidingExpiration, supplyVaule, autoRefresh);
            return cache.GetOrAddAsync(entry, cancellationToken);
        }
    }
}
