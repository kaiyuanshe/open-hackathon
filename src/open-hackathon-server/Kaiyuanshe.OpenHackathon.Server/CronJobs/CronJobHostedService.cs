using Autofac;
using Microsoft.Extensions.Hosting;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.CronJobs
{
    public class CronJobHostedService : IHostedService
    {
        private ILifetimeScope lifetimeScope;

        public CronJobHostedService(ILifetimeScope lifetimeScope)
        {
            this.lifetimeScope = lifetimeScope;
        }

        public async Task StartAsync(CancellationToken cancellationToken)
        {
            // start CronJobs
            var cronJobScheduler = lifetimeScope.Resolve<ICronJobScheduler>();
            await cronJobScheduler.ScheduleJobsAsync(lifetimeScope);
        }

        public Task StopAsync(CancellationToken cancellationToken)
        {
            return Task.CompletedTask;
        }
    }
}
