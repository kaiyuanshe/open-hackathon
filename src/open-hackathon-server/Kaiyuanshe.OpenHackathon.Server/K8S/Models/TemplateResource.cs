using Newtonsoft.Json;
using System.Collections.Generic;

namespace Kaiyuanshe.OpenHackathon.Server.K8S.Models
{
    /// <summary>
    /// Template resource definition.
    /// sample yaml: https://github.com/kaiyuanshe/cloudengine/blob/master/config/samples/hackathon_v1_template.yaml
    /// </summary>
    public class TemplateResource : CustomResource
    {
        // Properties of CustomResourceDefinition
        // See also: https://github.com/kaiyuanshe/cloudengine/blob/master/config/crd/bases/hackathon.kaiyuanshe.cn_templates.yaml
        public static readonly string Group = "hackathon.kaiyuanshe.cn";
        public static readonly string Version = "v1";
        public static readonly string Plural = "templates";
        public static readonly string API_VERSION = "hackathon.kaiyuanshe.cn/v1";

        [JsonProperty(PropertyName = "data")]
        public TemplateData Data { get; set; }
    }

    public class TemplateData
    {
        [JsonProperty(PropertyName = "type")]
        public string Type { get; set; }

        [JsonProperty(PropertyName = "podTemplate")]
        public PodTemplate PodTemplate { get; set; }

        [JsonProperty(PropertyName = "ingressProtocol")]
        public string IngressProtocol { get; set; }

        [JsonProperty(PropertyName = "ingressPort")]
        public int IngressPort { get; set; }

        [JsonProperty(PropertyName = "vnc")]
        public VncConnection VncConnection { get; set; }
    }

    public class PodTemplate
    {
        [JsonProperty(PropertyName = "image")]
        public string Image { get; set; }

        [JsonProperty(PropertyName = "command")]
        public string[] Command { get; set; }

        [JsonProperty(PropertyName = "env")]
        public IDictionary<string, string> EnvironmentVariables { get; set; }
    }

    public class VncConnection
    {
        [JsonProperty(PropertyName = "username")]
        public string Username { get; set; }

        [JsonProperty(PropertyName = "password")]
        public string Password { get; set; }
    }
}
