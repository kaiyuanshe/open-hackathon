using Autofac;
using Microsoft.Extensions.Logging;
using Quartz;
using Quartz.Logging;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.CronJobs
{
    public interface ICronJobScheduler
    {
        Task ScheduleJobsAsync(ILifetimeScope container);
    }

    public class CronJobScheduler : ICronJobScheduler
    {
        private readonly ILogger Logger;

        public CronJobScheduler(ILogger<CronJobScheduler> logger)
        {
            Logger = logger;
        }

        public async Task ScheduleJobsAsync(ILifetimeScope container)
        {
            Logger.LogInformation($"Scheduling Cron Jobs:");
            IList<ICronJob> jobs = new List<ICronJob>();
            foreach (var cronJobType in typeof(ICronJob).SubTypes())
            {
                ICronJob cronJob = (ICronJob)container.Resolve(cronJobType);
                jobs.Add(cronJob);
            }

            await ScheduleJobsAsync(container, jobs);
        }

        public async Task ScheduleJobsAsync(ILifetimeScope container, IEnumerable<ICronJob> jobs)
        {
            LogProvider.SetCurrentLogProvider(new LogAdapter(Logger));

            // construct a scheduler factory
            var factory = container.Resolve<CronJobSchedulerFactory>();
            // get a scheduler
            IScheduler scheduler = await factory.GetScheduler();
            await scheduler.Start();

            // Add jobs
            foreach (var job in jobs)
            {
                string jobName = job.GetType().Name;
                IJobDetail jobdetail = JobBuilder.Create(job.GetType())
                    .WithIdentity(jobName)
                    .UsingJobData(job.JobDataMap)
                    .Build();
                await scheduler.ScheduleJob(jobdetail, job.Trigger);
                Logger.LogInformation($"[ScheduleJobsAsync]Job {jobName} Scheduled.");
            }
        }

        class LogAdapter : ILogProvider
        {
            ILogger logger;
            public LogAdapter(ILogger logger)
            {
                this.logger = logger;
            }

            public Logger GetLogger(string name)
            {
                return (level, func, exception, parameters) =>
                {
                    if (func != null && logger != null)
                    {
                        string trace = string.Format("[Quartz]" + func(), parameters);
                        Action<string, object[]> action = logger.LogInformation;
                        switch (level)
                        {
                            case Quartz.Logging.LogLevel.Trace:
                            case Quartz.Logging.LogLevel.Debug:
                                action = logger.LogDebug;
                                break;
                            case Quartz.Logging.LogLevel.Warn:
                                action = logger.LogWarning;
                                break;
                            case Quartz.Logging.LogLevel.Error:
                                action = logger.LogError;
                                break;
                            case Quartz.Logging.LogLevel.Fatal:
                                action = logger.LogCritical;
                                break;
                        }
                        logger.LogInformation(trace);
                    }
                    return true;
                };
            }

            public IDisposable OpenMappedContext(string key, object value, bool destructure = false)
            {
                throw new NotImplementedException();
            }

            public IDisposable OpenNestedContext(string message)
            {
                throw new NotImplementedException();
            }
        }
    }
}
