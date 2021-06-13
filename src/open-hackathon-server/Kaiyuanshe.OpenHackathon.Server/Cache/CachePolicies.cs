using System;
using System.Runtime.Caching;

namespace Kaiyuanshe.OpenHackathon.Server.Cache
{
    public static class CachePolicies
    {
        /// <summary>
        /// Cache entry evicted in 10 minutes.
        /// </summary>
        public static CacheItemPolicy ExpireIn10M = new CacheItemPolicy
        {
            AbsoluteExpiration = DateTimeOffset.UtcNow.AddMinutes(10)
        };

        /// <summary>
        /// Cache entry evicted in 10 minutes.
        /// </summary>
        public static CacheItemPolicy ExpireIn1M = new CacheItemPolicy
        {
            AbsoluteExpiration = DateTimeOffset.UtcNow.AddMinutes(1)
        };
    }
}
