using Newtonsoft.Json;
using System.ComponentModel.DataAnnotations;

namespace Kaiyuanshe.OpenHackathon.Server.Models
{
    /// <summary>
    /// FileUpload
    /// </summary>
    public class FileUpload
    {
        /// <summary>
        /// SAS token expiration time. 2 minutes by default.
        /// </summary>
        /// <example>3</example>
        [Range(2, 30)]
        public int? expiration { get; set; }

        /// <summary>
        /// The name of the file to upload to the blob.
        /// </summary>
        /// <example>avatar.jpg</example>
        [Required]
        [MaxLength(256)]
        public string filename { get; set; }
    }
}
