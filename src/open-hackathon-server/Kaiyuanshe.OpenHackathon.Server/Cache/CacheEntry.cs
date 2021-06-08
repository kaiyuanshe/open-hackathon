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
        public CacheEntryType CacheEntryType { get; protected set; }

        /// <summary>
        /// sub key in each CacheEntryType. The full cache key is of format `{CacheEntryType}-{SubCacheKeyk}`
        /// </summary>
        public string SubCacheKey { get; protected set; }

        /// <summary>
        /// Unique Key to set/retrive data in Cache provider
        /// </summary>
        public string CacheKey
        {
            get
            {
                return $"{CacheEntryType}-{SubCacheKey}";
            }
        }

        public CacheItemPolicy CachePolicy { get; protected set; }

        public abstract bool AutoRefresh { get; }

    }

    public class CacheEntry<TValue> : CacheEntry
    {
        /// <summary>
        /// Func to supply value if not found in cache.
        /// </summary>
        private Func<CancellationToken, Task<TValue>> supplyValueAsync;
        private bool autoRefresh;

        public CacheEntry(CacheEntryType cacheEntryType, string subCacheKey, bool autoRefresh, CacheItemPolicy policy, Func<CancellationToken, Task<TValue>> supplyValue)
        {
            if (subCacheKey == null)
                throw new ArgumentNullException(nameof(subCacheKey));
            if (policy == null)
                throw new ArgumentNullException(nameof(policy));
            if (supplyValue == null)
                throw new ArgumentNullException(nameof(supplyValue));

            CacheEntryType = cacheEntryType;
            SubCacheKey = subCacheKey;
            this.autoRefresh = autoRefresh;
            CachePolicy = policy;
            supplyValueAsync = supplyValue;
        }

        public override bool AutoRefresh => autoRefresh;

        public async Task<TValue> SupplyValueAsync(CancellationToken cancellationToken)
        {
            return await supplyValueAsync(cancellationToken);
        }
    }
}
