using Autofac;
using Kaiyuanshe.OpenHackathon.Server.Storage;

namespace Kaiyuanshe.OpenHackathon.Server.DependencyInjection
{
    public class HackathonDefaultModule : Module
    {
        protected override void Load(ContainerBuilder builder)
        {
            builder.RegisterType<Weather>().As<IWeather>().PropertiesAutowired();
            builder.RegisterType<DefaultStorageAccountProvider>().As<IStorageAccountProvider>().PropertiesAutowired().SingleInstance();
            builder.RegisterType<StorageContext>().As<IStorageContext>().PropertiesAutowired().SingleInstance();
        }
    }
}
