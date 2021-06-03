using Autofac;
using Quartz;
using Quartz.Core;
using Quartz.Impl;
using Quartz.Spi;
using System;

namespace Kaiyuanshe.OpenHackathon.Server.CronJobs
{
    /// <summary>
    /// a class to override the default Quartz factory to allow Autofac DI.
    /// </summary>
    public class CronJobFactory : IJobFactory
    {
        public ILifetimeScope LifetimeScope { get; set; }

        public IJob NewJob(TriggerFiredBundle bundle, IScheduler scheduler)
        {
            if (bundle == null) throw new ArgumentNullException(nameof(bundle));
            if (scheduler == null) throw new ArgumentNullException(nameof(scheduler));

            var jobType = bundle.JobDetail.JobType;
            return (IJob)LifetimeScope.Resolve(jobType);
        }

        public void ReturnJob(IJob job)
        {

        }
    }

    /// <summary>
    /// a class to override the default SchedulerFactory to allow Autofac DI
    /// </summary>
    public class CronJobSchedulerFactory : StdSchedulerFactory
    {
        CronJobFactory jobFactory;
        public CronJobSchedulerFactory(CronJobFactory jobFactory)
        {
            this.jobFactory = jobFactory;
        }

        protected override IScheduler Instantiate(QuartzSchedulerResources rsrcs, QuartzScheduler qs)
        {
            var scheduler = base.Instantiate(rsrcs, qs);
            scheduler.JobFactory = jobFactory;
            return scheduler;
        }
    }
}
