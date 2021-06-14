using Kaiyuanshe.OpenHackathon.Server.Cache;
using Microsoft.Extensions.Logging;
using System;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.CronJobs.Jobs
{
    public class RefreshCacheJob : CronJobBase
    {
        public ICacheProvider CacheProvider { get; set; }

        protected override TimeSpan Interval => TimeSpan.FromMinutes(1);

        protected override async Task ExecuteAsync(CronJobContext context, CancellationToken token)
        {
            Logger.LogInformation($"RefreshCacheJob triggered at {DateTime.UtcNow}");
            await CacheProvider.RefreshAllAsync(token);
        }
    }
}
