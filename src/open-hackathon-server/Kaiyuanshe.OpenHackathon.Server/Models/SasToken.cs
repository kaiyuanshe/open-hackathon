using Newtonsoft.Json;
using System.ComponentModel.DataAnnotations;

namespace Kaiyuanshe.OpenHackathon.Server.Models
{
    /// <summary>
    /// Shared Access Signature Token. Reference: https://docs.microsoft.com/en-us/azure/storage/common/storage-sas-overview
    /// </summary>
    public class SasToken
    {
        /// <summary>
        /// Token for SAS
        /// </summary>
        /// <example>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1ZWM3OGEyMGY4MjE2ZDRiNGEwYjQ3MjEi...</example>
        [Required]
        [MinLength(1)]
        [MaxLength(10240)]
        [JsonProperty("token")]
        public string token { get; set; }
    }
}
