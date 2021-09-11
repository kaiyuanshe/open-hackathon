using System;

namespace Kaiyuanshe.OpenHackathon.Server.Models
{
    public abstract class ModelBase
    {
        /// <summary>
        /// The UTC timestamp when it was created.
        /// </summary>
        /// <example>2008-01-14T04:33:35Z</example>
        public DateTime createdAt { get; internal set; }

        /// <summary>
        /// The UTC timestamp when the it was updated last time.
        /// </summary>
        /// <example>2008-01-14T04:33:35Z</example>
        public DateTime updatedAt { get; internal set; }
    }
}
