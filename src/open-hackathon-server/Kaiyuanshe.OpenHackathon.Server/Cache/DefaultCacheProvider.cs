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
        /// Refresh the cached value. Ignored if CacheEntry is not found.
        /// </summary>
        /// <param name="cacheEntryType"></param>
        /// <param name="subCacheKey"></param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        public Task RefreshAsync(CacheEntryType cacheEntryType, string subCacheKey, CancellationToken cancellationToken);

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

                var value = await cacheEntry.SupplyValueAsync(cancellationToken);
                cache.Add(cacheEntry.CacheKey, value, cacheEntry.CachePolicy);
            }
        }

        public async Task RefreshAsync(CacheEntryType cacheEntryType, string subCacheKey, CancellationToken cancellationToken)
        {
            if (cacheEntries.TryGetValue(CacheEntry.GetCacheKey(cacheEntryType, subCacheKey), out CacheEntry cacheEntry))
            {
                var value = await cacheEntry.SupplyValueAsync(cancellationToken);
                cache.Add(cacheEntry.CacheKey, value, cacheEntry.CachePolicy);
            }
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
}
