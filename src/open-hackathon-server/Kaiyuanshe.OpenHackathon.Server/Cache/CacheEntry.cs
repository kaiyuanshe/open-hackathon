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

        public CacheItemPolicy CachePolicy { get; protected set; }

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

        public CacheEntry(string cacheKey, CacheItemPolicy policy, Func<CancellationToken, Task<TValue>> supplyValue, bool autoRefresh)
        {
            if (cacheKey == null)
                throw new ArgumentNullException(nameof(cacheKey));
            if (policy == null)
                throw new ArgumentNullException(nameof(policy));
            if (supplyValue == null && !EnvHelper.IsRunningInTests())
                throw new ArgumentNullException(nameof(supplyValue));

            CacheKey = cacheKey;
            this.autoRefresh = autoRefresh;
            CachePolicy = policy;
            supplyValueAsync = supplyValue;
        }

        public override bool AutoRefresh => autoRefresh;

        public override async Task<object> SupplyValueAsync(CancellationToken cancellationToken)
        {
            return await supplyValueAsync(cancellationToken);
        }
    }
}
