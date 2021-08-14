using Microsoft.WindowsAzure.Storage.Table;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.Entities
{
    /// <summary>
    /// Entity for rating kinds. 
    /// PK: hackathonName.
    /// RK: Auto-generated Guid.
    /// </summary>
    public class RatingKindEntity : AdvancedTableEntity
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
        /// auto-generated Guid of kind. RowKey.
        /// </summary>
        [IgnoreProperty]
        public string Id
        {
            get
            {
                return RowKey;
            }
        }

        public string Name { get; set; }
        public string Description { get; set; }
        public int MaximumScore { get; set; }
    }
}
