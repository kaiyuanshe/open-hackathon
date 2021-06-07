using Microsoft.Extensions.Logging;
using System;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.CronJobs.Jobs
{
    public class SampleCronJob : CronJobBase
    {
        protected override TimeSpan Interval => TimeSpan.FromMinutes(1);

        protected override Task ExecuteAsync(CronJobContext context, CancellationToken token)
        {
            Logger.LogInformation($"Sample Job triggered at {DateTime.UtcNow}");

            return Task.CompletedTask;
        }
    }
}
