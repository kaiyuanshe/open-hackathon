using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using System;
using System.Collections.Generic;
using System.Runtime.Caching;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Cache
{
    public abstract class CacheEntry
    {
        /// <summary>
        /// Unique Key to set/retrive data in Cache provider
        /// </summary>
        public string CacheKey { get; protected set; }

        /// <summary>
        /// A span of time within which a cache entry must be accessed before the cache entry
        /// is evicted from the cache. The default is System.Runtime.Caching.ObjectCache.NoSlidingExpiration,
        /// meaning that the item should not be expired based on a time span.
        /// </summary>
        public TimeSpan SlidingExpiration { get; protected set; }

        public CacheItemPolicy CachePolicy
        {
            get
            {
                return new CacheItemPolicy
                {
                    SlidingExpiration = SlidingExpiration
                };
            }
        }

        public abstract bool AutoRefresh { get; }

        public abstract Task<object> SupplyValueAsync(CancellationToken cancellationToken);
    }

    public class CacheEntry<TValue> : CacheEntry
    {
        /// <summary>
        /// Func to supply value if not found in cache.
        /// </summary>
        private Func<CancellationToken, Task<TValue>> supplyValueAsync;
        private bool autoRefresh;

        public CacheEntry(string cacheKey, TimeSpan slidingExpiration, Func<CancellationToken, Task<TValue>> supplyValue, bool autoRefresh)
        {
            if (cacheKey == null)
                throw new ArgumentNullException(nameof(cacheKey));
            if (slidingExpiration == TimeSpan.MinValue)
                throw new ArgumentNullException(nameof(slidingExpiration));
            if (supplyValue == null && !EnvHelper.IsRunningInTests())
                throw new ArgumentNullException(nameof(supplyValue));

            CacheKey = cacheKey;
            this.autoRefresh = autoRefresh;
            SlidingExpiration = slidingExpiration;
            supplyValueAsync = supplyValue;
        }

        public override bool AutoRefresh => autoRefresh;

        public override async Task<object> SupplyValueAsync(CancellationToken cancellationToken)
        {
            return await supplyValueAsync(cancellationToken);
        }
    }
}
