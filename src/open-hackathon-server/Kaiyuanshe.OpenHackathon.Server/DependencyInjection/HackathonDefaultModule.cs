using Autofac;
using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.ResponseBuilder;
using Kaiyuanshe.OpenHackathon.Server.Storage;

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
            builder.RegisterType<UserManagement>().As<IUserManagement>().PropertiesAutowired().SingleInstance();
            builder.RegisterType<TeamManagement>().As<ITeamManagement>().PropertiesAutowired().SingleInstance();
            builder.RegisterType<AwardManagement>().As<IAwardManagement>().PropertiesAutowired().SingleInstance();

            // Response
            builder.RegisterType<DefaultResponseBuilder>().As<IResponseBuilder>().PropertiesAutowired().SingleInstance();
        }
    }
}
