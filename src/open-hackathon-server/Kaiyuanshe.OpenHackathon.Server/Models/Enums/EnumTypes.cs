using Newtonsoft.Json;
using Newtonsoft.Json.Converters;

namespace Kaiyuanshe.OpenHackathon.Server.Models.Enums
{
    /// <summary>
    /// Status of Hackathon
    /// </summary>
    public enum HackathonStatus
    {
        planning,
        pendingApproval,
        online,
        offline
    }
}
