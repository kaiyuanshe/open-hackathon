using Kaiyuanshe.OpenHackathon.Server.Storage;
using Microsoft.Extensions.Logging;
using Quartz;
using System;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.CronJobs
{
    public class CronJobContext
    {
        /// <summary>
        /// if true, won't execute until interval timespan goes by. If false, run it now no matter when job was run last time.
        /// </summary>
        public bool EnforceInterval { get; set; }

        /// <summary>
        /// Time when the current run is triggered
        /// </summary>
        public DateTime FireTime { get; set; }
    }

    public interface ICronJob : IJob
    {
        /// <summary>
        /// CronJob trigger. https://www.quartz-scheduler.net/documentation/quartz-3.x/tutorial/more-about-triggers.html#calendars
        /// </summary>
        ITrigger Trigger { get; }

        /// <summary>
        /// Get or set the Quartz.IJobDetail.JobDataMap that is associated with the Quartz.IJob.
        /// docs: https://www.quartz-scheduler.net/documentation/quartz-3.x/tutorial/more-about-jobs.html#jobdatamap
        /// </summary>
        JobDataMap JobDataMap { get; }

        /// <summary>
        /// Execute a CronJob immediately.
        /// </summary>
        /// <param name="context"></param>
        /// <returns></returns>
        Task ExecuteNow(CronJobContext context);
    }

    public abstract class CronJobBase : ICronJob
    {
        public IStorageContext StorageContext { get; set; }

        public ILoggerFactory LoggerFactory { get; set; }

        protected ILogger Logger
        {
            get
            {
                return LoggerFactory?.CreateLogger("CronJob");
            }
        }

        public virtual JobDataMap JobDataMap
        {
            get
            {
                return new JobDataMap();
            }
        }

        public Task Execute(IJobExecutionContext context)
        {
            CronJobContext cronJobContext = new CronJobContext
            {
                EnforceInterval = false,
                FireTime = context.FireTimeUtc.DateTime,
            };
            CancellationTokenSource cancellationTokenSource = new CancellationTokenSource();
            return ExecuteAsync(cronJobContext, cancellationTokenSource.Token);
        }

        public Task ExecuteNow(CronJobContext context)
        {
            CronJobContext cronJobContext = new CronJobContext
            {
                EnforceInterval = true,
                FireTime = DateTime.UtcNow,
            };
            CancellationTokenSource cancellationTokenSource = new CancellationTokenSource();
            return ExecuteAsync(cronJobContext, cancellationTokenSource.Token);
        }

        protected abstract Task ExecuteAsync(CronJobContext context, CancellationToken token);

        /// <summary>
        /// Interval between job runs
        /// </summary>
        protected abstract TimeSpan Interval { get; }
        public virtual ITrigger Trigger
        {
            get
            {
                var trigger = TriggerBuilder.Create()
                    .WithIdentity(GetType().Name)
                    .StartNow() // trigger it now
                    .WithSimpleSchedule(x => x.WithInterval(Interval).RepeatForever()) // execute forever with interval
                    .Build();
                return trigger;
            }
        }

    }
}
