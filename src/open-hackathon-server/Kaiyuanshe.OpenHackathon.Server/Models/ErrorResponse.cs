using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Models
{
    /// <summary>
    /// Contains information about an API error.
    /// </summary>
    public class ErrorResponse
    {
        /// <summary>
        /// Describes a particular API error with an error code and a message.
        /// </summary>
        public class ErrorResponseBody
        {
            /// <summary>
            /// An error code that describes the error condition more precisely than an HTTP status code. 
            /// Can be used to programmatically handle specific error cases.
            /// </summary>
            [JsonRequired]
            public string code { get; set; }

            /// <summary>
            /// A message that describes the error in detail and provides debugging information.
            /// </summary>
            [JsonRequired]
            public string message { get; set; }

            /// <summary>
            /// The target of the particular error (for example, the name of the property in error).
            /// </summary>
            [JsonProperty(NullValueHandling = NullValueHandling.Ignore)]
            public string target { get; set; }

            /// <summary>
            /// Contains nested errors that are related to this error.
            /// </summary>
            [JsonProperty(NullValueHandling = NullValueHandling.Ignore)]
            public IList<ErrorResponseBody> details { get; set; }
        }

        /// <summary>
        /// Describes a particular API error with an error code and a message.
        /// </summary>
        public ErrorResponseBody error { get; set; }


        /// <summary>
        /// Create a new ErrorResponse
        /// </summary>
        /// <param name="code">String that can be used to programmatically identify the error. 
        /// These error code is typically a string like “BadArgument”, “NotFound”, etc.</param>
        /// <param name="message">Describes the error in detail and provides debugging information.</param>
        /// <param name="target">The target of the particular error (for example, the name of the property in error).</param>
        /// <param name="details">An array of JSON objects that contain name/value pairs for code and message</param>
        /// <returns></returns>
        public static ErrorResponse Error(string code, string message, string target = null, IList<KeyValuePair<string, string>> details = null)
        {
            return new ErrorResponse
            {
                error = new ErrorResponseBody
                {
                    code = code,
                    message = message,
                    target = target,
                    details = details?.Select(detail =>
                    {
                        return new ErrorResponseBody
                        {
                            code = code,
                            message = detail.Value,
                            target = detail.Key,
                        };
                    }).ToArray(),
                },
            };
        }

        /// <summary>
        /// Create a BadArgument error response
        /// </summary>
        /// <returns>BadArgument error response</returns>
        public static ErrorResponse BadArgument(string message, string target = null, IList<KeyValuePair<string, string>> details = null)
        {
            return Error("BadArgument", message, target, details);
        }

        /// <summary>
        /// Create a NotFound error response
        /// </summary>
        /// <returns>NotFound error response</returns>
        public static ErrorResponse NotFound(string message, string target = null)
        {
            return Error("NotFound", message, target);
        }

        /// <summary>
        /// Create a Conflict error response
        /// </summary>
        /// <returns>Conflict error response</returns>
        public static ErrorResponse Conflict(string message)
        {
            return Error("Conflict", message);
        }

        /// <summary>
        /// Create a InternalServerError error response
        /// </summary>
        /// <returns></returns>
        public static ErrorResponse InternalServerError(string message)
        {
            return Error("InternalServerError", message);
        }

        /// <summary>
        /// Create a Forbidden(403) error response
        /// </summary>
        /// <returns></returns>
        public static ErrorResponse Forbidden(string message)
        {
            return Error("Forbidden", message);
        }
    }

}
