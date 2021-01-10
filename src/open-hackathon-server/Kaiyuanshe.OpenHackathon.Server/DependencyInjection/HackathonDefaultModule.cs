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
            builder.RegisterType<Weather>().As<IWeather>().PropertiesAutowired();
            // Storage
            builder.RegisterType<DefaultStorageAccountProvider>().As<IStorageAccountProvider>().PropertiesAutowired().SingleInstance();
            builder.RegisterType<StorageContext>().As<IStorageContext>().PropertiesAutowired().SingleInstance();

            //Biz
            builder.RegisterType<HackathonManager>().As<IHackathonManager>().PropertiesAutowired().SingleInstance();

            // Response
            builder.RegisterType<DefaultResponseBuilder>().As<IResponseBuilder>().PropertiesAutowired().SingleInstance();
        }
    }
}
