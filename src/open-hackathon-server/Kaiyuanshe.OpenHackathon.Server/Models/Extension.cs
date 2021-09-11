using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Models
{
    /// <summary>
    /// Extra properties, typically name-value pairs.
    /// </summary>
    public class Extension
    {
        /// <summary>
        /// name of the extension.
        /// </summary>
        /// <example>mykey</example>
        [Required]
        [MaxLength(128)]
        public string name { get; set; }

        /// <summary>
        /// value of the extension
        /// </summary>
        /// <example>myvalue</example>
        [Required]
        [MaxLength(1024)]
        public string value { get; set; }
    }

    public static class ExtensionHelper
    {
        public static Extension[] Merge(this Extension[] extensions, Extension[] updates)
        {
            if (extensions == null)
            {
                extensions = new Extension[0];
            }
            if (updates == null)
            {
                updates = new Extension[0];
            }

            List<Extension> results = new List<Extension>();

            foreach (var ext in extensions.Concat(updates).Reverse())
            {
                if (results.Any(r => r.name == ext.name))
                    continue;

                results.Add(ext);
            }

            results.Reverse();
            return results.ToArray();
        }
    }
}
