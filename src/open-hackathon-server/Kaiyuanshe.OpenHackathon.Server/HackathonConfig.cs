using Microsoft.Extensions.Configuration;
using System;

namespace Kaiyuanshe.OpenHackathon.Server
{
    [Flags]
    public enum ConfigSource
    {
        Config,
        KeyVault,
        All = 255,
    }

    public static class HackathonConfigKeys
    {
        public static class Storage
        {
            public static readonly string ConnectionString = "";
        }
    }

    public interface IHackathonConfig
    {
        T GetConfig<T>(string key, T defaultVaule = default, ConfigSource configSource = ConfigSource.All);
    }

    public class HackathonConfig : IHackathonConfig
    {

        IConfiguration _configuration;
        public HackathonConfig(IConfiguration configuration)
        {
            _configuration = configuration;
        }

        public T GetConfig<T>(string key, T defaultVaule = default, ConfigSource configSource = ConfigSource.All)
        {
            if (configSource.HasFlag(ConfigSource.Config))
            {
                try
                {
                    string value = _configuration[key];
                    if (value != null)
                    {
                        return (T)Convert.ChangeType(value, typeof(T));
                    }
                }
                catch
                {
                }
            }

            if (configSource.HasFlag(ConfigSource.KeyVault))
            {
                // TODO
            }

            return defaultVaule;
        }
    }
}
