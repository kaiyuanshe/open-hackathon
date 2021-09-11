using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Models
{
    /// <summary>
    /// Check the name availability
    /// </summary>
    public class NameAvailability
    {
        /// <summary>
        /// name of hackathon
        /// </summary>
        /// <example>foo</example>
        [Required]
        public string name { get; set; }

        /// <summary>
        /// Indicates whether the name is available or not.
        /// </summary>
        /// <example>true</example>
        public bool nameAvailable { get; internal set; }

        /// <summary>
        /// The reason of the availability. Required if name is not available.
        /// </summary>
        /// <example>AlreadyExists</example>
        [JsonProperty(NullValueHandling = NullValueHandling.Ignore)]
        public string reason { get; internal set; }

        /// <summary>
        /// The message of the operation.
        /// </summary>
        /// <example>AlreadyExists</example>
        [JsonProperty(NullValueHandling = NullValueHandling.Ignore)]
        public string message { get; internal set; }

        public NameAvailability OK()
        {
            return new NameAvailability
            {
                name = name,
                nameAvailable = true
            };
        }

        public NameAvailability Invalid(string message)
        {
            return Failed("Invalid", message);
        }

        public NameAvailability AlreadyExists(string message)
        {
            return Failed("AlreadyExists", message);
        }

        NameAvailability Failed(string reason, string message)
        {
            return new NameAvailability
            {
                name = name,
                nameAvailable = false,
                reason = reason,
                message = message
            };
        }
    }
}
