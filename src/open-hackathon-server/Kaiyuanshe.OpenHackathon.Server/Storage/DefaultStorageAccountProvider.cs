using Microsoft.Extensions.Configuration;
using Microsoft.WindowsAzure.Storage;

namespace Kaiyuanshe.OpenHackathon.Server.Storage
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

        public DefaultStorageAccountProvider(IConfiguration configuration)
        {
            connectionString = configuration["Storage:Hackathon:ConnectionString"];
        }

        public CloudStorageAccount HackathonServerStorage => CloudStorageAccount.Parse(connectionString);
    }
}
