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
        /// <example>reFh8jikl%2B2hOVhJ5SORPkItoFN6Y8bbq%2FeYgKn6QsI%3D</example>
        [Required]
        [MinLength(1)]
        [MaxLength(10240)]
        [JsonProperty("token")]
        public string token { get; set; }
    }
}
