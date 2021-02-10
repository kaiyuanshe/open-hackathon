using Kaiyuanshe.OpenHackathon.Server.Storage;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Biz
{
    public abstract class ManagementClientBase
    {
        public IStorageContext StorageContext { get; set; }
    }
}
