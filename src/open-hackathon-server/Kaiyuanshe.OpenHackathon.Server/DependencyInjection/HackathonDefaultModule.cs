using Autofac;
using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Cache;
using Kaiyuanshe.OpenHackathon.Server.CronJobs;
using Kaiyuanshe.OpenHackathon.Server.K8S;
using Kaiyuanshe.OpenHackathon.Server.ResponseBuilder;
using Kaiyuanshe.OpenHackathon.Server.Storage;
using Quartz;
using Quartz.Spi;

namespace Kaiyuanshe.OpenHackathon.Server.DependencyInjection
{
    public class HackathonDefaultModule : Module
    {
        protected override void Load(ContainerBuilder builder)
        {
            // Storage
            builder.RegisterType<DefaultStorageAccountProvider>().As<IStorageAccountProvider>().PropertiesAutowired().SingleInstance();
            builder.RegisterType<StorageContext>().As<IStorageContext>().PropertiesAutowired().SingleInstance();

            //Biz
            builder.RegisterType<HackathonManagement>().As<IHackathonManagement>().PropertiesAutowired().SingleInstance();
            builder.RegisterType<EnrollmentManagement>().As<IEnrollmentManagement>().PropertiesAutowired().SingleInstance();
            builder.RegisterType<HackathonAdminManagement>().As<IHackathonAdminManagement>().PropertiesAutowired().SingleInstance();
            builder.RegisterType<UserManagement>().As<IUserManagement>().PropertiesAutowired().SingleInstance();
            builder.RegisterType<TeamManagement>().As<ITeamManagement>().PropertiesAutowired().SingleInstance();
            builder.RegisterType<AwardManagement>().As<IAwardManagement>().PropertiesAutowired().SingleInstance();
            builder.RegisterType<FileManagement>().As<IFileManagement>().PropertiesAutowired().SingleInstance();
            builder.RegisterType<WorkManagement>().As<IWorkManagement>().PropertiesAutowired().SingleInstance();
            builder.RegisterType<JudgeManagement>().As<IJudgeManagement>().PropertiesAutowired().SingleInstance();
            builder.RegisterType<RatingManagement>().As<IRatingManagement>().PropertiesAutowired().SingleInstance();
            builder.RegisterType<ExperimentManagement>().As<IExperimentManagement>().PropertiesAutowired().SingleInstance();

            // Kubernetes
            builder.RegisterType<KubernetesConfigProvider>().As<IKubernetesConfigProvider>().PropertiesAutowired().SingleInstance();
            builder.RegisterType<KubernetesClusterFactory>().As<IKubernetesClusterFactory>().PropertiesAutowired().SingleInstance();

            // Response
            builder.RegisterType<DefaultResponseBuilder>().As<IResponseBuilder>().PropertiesAutowired().SingleInstance();

            // Cache
            builder.RegisterType<DefaultCacheProvider>().As<ICacheProvider>().PropertiesAutowired().SingleInstance();

            // CronJob
            builder.RegisterTypes(typeof(ICronJob).SubTypes()).SingleInstance().PropertiesAutowired();
            builder.RegisterType<CronJobFactory>().AsSelf().As<IJobFactory>().SingleInstance().PropertiesAutowired();
            builder.RegisterType<CronJobSchedulerFactory>().AsSelf().As<ISchedulerFactory>().SingleInstance().PropertiesAutowired();
            builder.RegisterType<CronJobScheduler>().As<ICronJobScheduler>().SingleInstance().PropertiesAutowired();
        }
    }
}
