using Newtonsoft.Json;
using System.ComponentModel.DataAnnotations;

namespace Kaiyuanshe.OpenHackathon.Server.Models
{
    /// <summary>
    /// Information of a file upload request. You cannot upload a file via hackathon API,
    /// instead Hackathon API returns backend storage URLs where you can talk to the file stroage directly through these Urls.
    /// </summary>
    public class FileUpload
    {
        /// <summary>
        /// Expected Upload Url expiration time in minutes. 5 minutes by default.
        /// </summary>
        /// <example>5</example>
        [Range(2, 30)]
        public int? expiration { get; set; }

        /// <summary>
        /// The name of the file to upload.
        /// </summary>
        /// <example>avatar.png</example>
        [Required]
        [MaxLength(256)]
        public string filename { get; set; }

        /// <summary>
        /// absolute Url with write access to upload the file. The Url contains a SAS token which expires in certain minutes.
        /// Learn more about SAS token at Reference: https://docs.microsoft.com/en-us/azure/storage/common/storage-sas-overview.
        /// </summary>
        /// <example>https://storagename.blob.core.chinacloudapi.cn/$web/user/2020/01/01/avatar.png?sv=2018-03-28&amp;sr=b&amp;sig=JT1H%2FcjWK1xbwK3gy1qXXbXAxuQBTmYoCwpmK2Z9Ls0%3D&amp;st=2021-07-04T09%3A25%3A39Z&amp;se=2021-07-04T09%3A32%3A39Z&amp;sp=rw</example>
        public string uploadUrl { get; internal set; }

        /// <summary>
        /// absolute readOnly url.
        /// </summary>
        /// <example>https://hackathon-api.static.kaiyuanshe.cn/user/2020/01/01/avatar.png</example>
        public string url { get; internal set; }
    }
}
