using System;
using System.Runtime.Caching;
using System.Runtime.CompilerServices;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server
{
    public static class CacheHelper
    {
        static MemoryCache cache = MemoryCache.Default;

        public static T GetOrAdd<T>(string key, Func<T> supplyValue, CacheItemPolicy policy)
        {
            // disable cache in Dev or Unit Tests
            if (EnvHelper.IsDevelopment() || EnvHelper.IsRunningInTests())
            {
                return supplyValue();
            }

            return GetOrAddInternal(key, () => Task.FromResult(supplyValue()), policy).Result;
        }

        public async static Task<T> GetOrAddAsync<T>(string key, Func<Task<T>> supplyValue, CacheItemPolicy policy)
        {
            // disable cache in Dev or Unit Tests
            if (EnvHelper.IsDevelopment() || EnvHelper.IsRunningInTests())
            {
                return await supplyValue();
            }

            return await GetOrAddInternal(key, supplyValue, policy);
        }

        internal static async Task<T> GetOrAddInternal<T>(string key, Func<Task<T>> supplyValue, CacheItemPolicy policy)
        {
            if (!cache.Contains(key))
            {
                var value = await supplyValue();
                if (value != null)
                {
                    cache.Add(key, value, policy);
                    return value;
                }
                else
                {
                    return default(T);
                }
            }
            else
            {
                return (T)cache[key];
            }
        }

        public static void Remove(string key)
        {
            cache.Remove(key);
        }
    }
}
