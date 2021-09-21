using k8s.Models;
using Newtonsoft.Json;

namespace Kaiyuanshe.OpenHackathon.Server.K8S.Models
{
    /// <summary>
    /// Experiment resource definition.
    /// Sample yaml: https://github.com/kaiyuanshe/cloudengine/blob/master/config/samples/hackathon_v1_experiment.yaml
    /// </summary>
    public class ExperimentResource : CustomResource<ExperimentSpec, ExperimentStatus>
    {
    }

    public class ExperimentSpec
    {
        [JsonProperty(PropertyName = "pause")]
        public bool Pause { get; set; }

        [JsonProperty(PropertyName = "template")]
        public string TemplateName { get; set; }

        [JsonProperty(PropertyName = "clusterName")]
        public string ClusterName { get; set; }
    }

    public class ExperimentStatus : V1Status
    {
        [JsonProperty(PropertyName = "cluster")]
        public string ClusterName { get; set; }

        [JsonProperty(PropertyName = "ingressIPs")]
        public string[] IngressIPs { get; set; }

        [JsonProperty(PropertyName = "ingressPort")]
        public int ingressPort { get; set; }

        [JsonProperty(PropertyName = "protocol")]
        public string IngressProtocol { get; set; }

        [JsonProperty(PropertyName = "vnc")]
        public VncConnection VncConnection { get; set; }
    }
}
