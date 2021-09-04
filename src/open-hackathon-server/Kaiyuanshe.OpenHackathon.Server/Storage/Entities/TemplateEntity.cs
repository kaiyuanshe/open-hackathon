using Kaiyuanshe.OpenHackathon.Server.Models;
using Microsoft.WindowsAzure.Storage.Table;
using System.Collections.Generic;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.Entities
{
    /// <summary>
    /// Template for hackathon experiment.
    /// PK: hackathon
    /// RK: template name
    /// </summary>
    public class TemplateEntity : AdvancedTableEntity
    {
        /// <summary>
        /// name of Hackathon. PartitionKey
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
        /// name of template. RowKey.
        /// </summary>
        [IgnoreProperty]
        public string Name
        {
            get
            {
                return RowKey;
            }
        }

        /// <summary>
        /// Container image.
        /// </summary>
        public string Image { get; set; }

        /// <summary>
        /// commands to start a container.
        /// </summary>
        public string[] Commands { get; set; }

        /// <summary>
        /// environment variables passed to the container.
        /// </summary>
        public Dictionary<string, string> EnvironmentVariables { get; set; }

        /// <summary>
        /// protocol for remote connection
        /// </summary>
        /// <example>vnc</example>
        public IngressProtocol IngressProtocol { get; set; }

        /// <summary>
        /// Port for remote connection
        /// </summary>
        /// <example>5901</example>
        public int IngressPort { get; set; }

        /// <summary>
        /// login user name for remote connection. lowercase chars and numbers only: ^[a-z][a-z0-9]{1, 63}$
        /// </summary>
        public string UserName { get; set; }
    }
}
