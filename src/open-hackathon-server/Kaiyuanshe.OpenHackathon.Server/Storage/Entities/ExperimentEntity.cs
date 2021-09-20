using Microsoft.WindowsAzure.Storage.Table;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.Entities
{
    /// <summary>
    /// Entity for Experiment. 
    /// PK: hackathonName.
    /// RK: auto-generated Guid.
    /// </summary>
    public class ExperimentEntity : AdvancedTableEntity
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
        /// id of experiment. RowKey
        /// </summary>
        [IgnoreProperty]
        public string Id
        {
            get
            {
                return RowKey;
            }
        }

        public string TemplateName { get; set; }

        public string UserId { get; set; }

        /// <summary>
        /// paused. retained for future use. `false` for now.
        /// </summary>
        public bool Paused { get; set; }
    }
}
