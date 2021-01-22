using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.Entities
{
    /// <summary>
    /// Token
    /// 
    /// PartitionKey: token
    /// RowKey: string.Empty
    /// </summary>
    public class UserTokenEntity : AdvancedTableEntity
    {
        public string UserId { get; set; }

        public string Token
        {
            get
            {
                return PartitionKey;
            }
        }

        public DateTime TokenExpiredAt { get; set; }
    }
}
