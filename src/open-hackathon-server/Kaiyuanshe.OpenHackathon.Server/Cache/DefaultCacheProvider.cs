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
    }

    public class DefaultCacheProvider : ICacheProvider
    {
        static MemoryCache cache = MemoryCache.Default;
        static Dictionary<string, CacheEntry> cacheEntries = new Dictionary<string, CacheEntry>();

        public async Task<TValue> GetOrAddAsync<TValue>(CacheEntry<TValue> cacheEntry, CancellationToken cancellationToken)
        {
            // disable cache in Dev or Unit Tests
            if (EnvHelper.IsDevelopment() || EnvHelper.IsRunningInTests())
            {
                return await cacheEntry.SupplyValueAsync(cancellationToken);
            }

            cacheEntries[cacheEntry.CacheKey] = cacheEntry;
            return await CacheHelper.GetOrAddAsync(
                cacheEntry.CacheKey,
                async () =>
                {
                    return await cacheEntry.SupplyValueAsync(cancellationToken);
                },
                cacheEntry.CachePolicy);
        }

        public Task RefreshAsync(CacheEntryType cacheEntryType, string subCacheKey, CancellationToken cancellationToken)
        {
            throw new NotImplementedException();
        }
    }
}
