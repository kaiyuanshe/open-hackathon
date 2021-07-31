using Microsoft.WindowsAzure.Storage.Table;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.Entities
{
    /// <summary>
    /// Entity of a hackathon judge.
    /// 
    /// PK: hackathon name.
    /// RK: userId.
    /// </summary>
    public class JudgeEntity : AdvancedTableEntity
    {
        /// <summary>
        /// name of Hackathon, PartitionKey
        /// </summary>
        [IgnoreProperty]
        public string HackathonName
        {
            get
            {
                return PartitionKey;
            }
        }

        /// <summary>
        /// id of User. RowKey
        /// </summary>
        [IgnoreProperty]
        public string UserId
        {
            get
            {
                return RowKey;
            }
        }

        /// <summary>
        /// description of the Judge
        /// </summary>
        /// <example>Professor of Computer Science, Tsinghua University</example>
        public string Description { get; set; }
    }
}
