using Newtonsoft.Json;
using System.ComponentModel.DataAnnotations;

namespace Kaiyuanshe.OpenHackathon.Server.Models
{
    /// <summary>
    /// Shared Access Signature Token. Reference: https://docs.microsoft.com/en-us/azure/storage/common/storage-sas-overview
    /// </summary>
    public class SasUrl
    {
        /// <summary>
        /// SAS URL
        /// </summary>
        /// <example>https://container.blob.core.chinacloudapi.cn/kysuser/user/avatar.jpeg?sv=2018-03-28&amp;sr=b&amp;sig=JT1H%2FcjWK1xbwK3gy1qXXbXAxuQBTmYoCwpmK2Z9Ls0%3D&amp;st=2021-07-04T09%3A25%3A39Z&amp;se=2021-07-04T09%3A32%3A39Z&amp;sp=rw</example>
        [JsonProperty("url")]
        public string url { get; set; }
    }
}
