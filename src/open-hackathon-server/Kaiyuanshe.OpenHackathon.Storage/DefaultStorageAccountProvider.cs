using Kaiyuanshe.OpenHackathon.Common;
using Microsoft.WindowsAzure.Storage;

namespace Kaiyuanshe.OpenHackathon.Storage
{
    public interface IStorageAccountProvider
    {
        /// <summary>
        /// Major storage account used by OPH APIs.
        /// </summary>
        CloudStorageAccount HackathonServerStorage { get; }
    }

    /// <summary>
    /// Default impl. Read Storage Account Connection String from Config.
    /// </summary>
    public class DefaultStorageAccountProvider : IStorageAccountProvider
    {
        string connectionString;

        public DefaultStorageAccountProvider(IHackathonConfig hackathonConfig)
        {
            connectionString = hackathonConfig.GetConfig(HackathonConfigKeys.Storage.ConnectionString, "UseDevelopmentStorage=true");
        }

        public CloudStorageAccount HackathonServerStorage => CloudStorageAccount.Parse(connectionString);
    }
}
