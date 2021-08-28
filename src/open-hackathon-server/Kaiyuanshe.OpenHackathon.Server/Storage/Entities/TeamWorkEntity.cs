using Kaiyuanshe.OpenHackathon.Server.Models;
using Microsoft.WindowsAzure.Storage.Table;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.Entities
{
    /// <summary>
    /// Entity of TeamWork.
    /// 
    /// PK: HackathonName.
    /// RK: auto-generated GUID
    /// </summary>
    public class TeamWorkEntity : AdvancedTableEntity
    {
        /// <summary>
        /// PartitionKey
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
        /// RowKey
        /// </summary>
        [IgnoreProperty]
        public string Id
        {
            get
            {
                return RowKey;
            }
        }

        public string TeamId { get; set; }

        public string Title { get; set; }

        public string Description { get; set; }

        public TeamWorkType Type { get; set; }

        public string Url { get; set; }
    }
}
