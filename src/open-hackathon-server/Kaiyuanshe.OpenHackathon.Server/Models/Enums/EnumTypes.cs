using Newtonsoft.Json;
using Newtonsoft.Json.Converters;

namespace Kaiyuanshe.OpenHackathon.Server.Models.Enums
{
    /// <summary>
    /// Status of Hackathon
    /// </summary>
   [JsonConverter(typeof(StringEnumConverter))]
    public enum HackathonStatus
    {
        Planning,
        PendingApproval,
        Online,
        Offline
    }
}
