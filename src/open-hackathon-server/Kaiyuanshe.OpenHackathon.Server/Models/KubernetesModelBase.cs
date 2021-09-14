using k8s.Models;

namespace Kaiyuanshe.OpenHackathon.Server.Models
{
    public abstract class KubernetesModelBase : ModelBase
    {
        /// <summary>
        /// Status of the object in kubernetes
        /// </summary>
        public Status status { get; internal set; }
    }

    /// <summary>
    /// Status of kubernetes resources, a subset of kubernetes.V1Status
    /// </summary>
    public class Status
    {
        /// <summary>
        /// A machine-readable description of why this operation is in the "Failure" status.
        /// If this value is empty there is no information available. A Reason clarifies
        /// an HTTP status code but does not override it.
        /// </summary>
        /// <example>AlreadyExists</example>
        public string reason { get; set; }

        /// <summary>
        /// A human-readable description of the status of this operation.
        /// </summary>
        /// <example>The resource already exists.</example>
        public string message { get; set; }

        /// <summary>
        /// Kind is a string value representing the REST resource this object represents.
        /// Servers may infer this from the endpoint the client submits requests to. Cannot
        /// be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds
        /// </summary>
        /// <example>status</example>
        public string kind { get; set; }

        /// <summary>
        /// Extended data associated with the reason. Each reason may define its own extended
        /// details. This field is optional and the data returned is not guaranteed to conform
        /// to any schema except that defined by the reason type.
        /// </summary>
        public V1StatusDetails details { get; set; }

        /// <summary>
        /// Status of the operation. One of: "Success" or "Failure". More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#spec-and-status
        /// </summary>
        /// <example>success</example>
        public string status { get; set; }

        /// <summary>
        /// Suggested HTTP return code for this status, 0 if not set.
        /// </summary>
        /// <example>200</example>
        public int? code { get; set; }

        public static Status FromV1Status(V1Status v1Status)
        {
            return v1Status.As<Status>();
        }
    }
}
