using System;
using System.Collections.Generic;
using System.Text;

namespace Kaiyuanshe.OpenHackathon.Storage.Entities
{
    /// <summary>
    /// Hackathons.
    /// </summary>
    public class HackathonEntity : AdvancedTableEntity
    {
        public string DisplayName { get; set; }
    }
}
