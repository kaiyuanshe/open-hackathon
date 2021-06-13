using Kaiyuanshe.OpenHackathon.Server.Cache;
using Kaiyuanshe.OpenHackathon.Server.Storage;

namespace Kaiyuanshe.OpenHackathon.Server.Biz
{
    public abstract class ManagementClientBase
    {
        public IStorageContext StorageContext { get; set; }

        public ICacheProvider Cache { get; set; }
    }
}
