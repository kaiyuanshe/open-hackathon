using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.Entities
{
    /// <summary>
    /// Token
    /// 
    /// PartitionKey: id(from Authing). Globally unique.
    /// RowKey: string.Empty
    /// </summary>
    public class UserTokenEntity : AdvancedTableEntity
    {
        public string UserId { 
            get
            {
                return PartitionKey;
            } 
        }

        public string Token { get; set; }

        public DateTime TokenExpiredAt { get; set; }
    }
}
