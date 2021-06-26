using Newtonsoft.Json;
using System.ComponentModel.DataAnnotations;

namespace Kaiyuanshe.OpenHackathon.Server.Models
{
    /// <summary>
    /// SAS Expiration Time
    /// </summary>
    public class SasExpiration
    {
        /// <summary>
        /// SAS token expiration time. 2 by default.
        /// </summary>
        /// <example>3</example>
        [Range(2, 30)]
        public int? expiration { get; set; }
    }
}
