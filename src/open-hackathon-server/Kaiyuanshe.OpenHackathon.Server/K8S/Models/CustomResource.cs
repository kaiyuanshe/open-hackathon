using k8s;
using k8s.Models;
using Newtonsoft.Json;

namespace Kaiyuanshe.OpenHackathon.Server.K8S.Models
{
    public abstract class CustomResource : KubernetesObject
    {
        [JsonProperty(PropertyName = "metadata")]
        public V1ObjectMeta Metadata { get; set; }
    }

    public abstract class CustomResource<TSpec, TStatus> : CustomResource
    {
        [JsonProperty(PropertyName = "spec")]
        public TSpec Spec { get; set; }

        [JsonProperty(PropertyName = "status")]
        public TStatus Status { get; set; }
    }
}
