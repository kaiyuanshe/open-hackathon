using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using System.Collections.Generic;

namespace Kaiyuanshe.OpenHackathon.Server.K8S.Models
{
    public class TemplateContext
    {
        public TemplateEntity TemplateEntity { get; set; }

        public TemplateResource BuildCustomResource()
        {
            var env = TemplateEntity.EnvironmentVariables ?? new Dictionary<string, string>();
            if (TemplateEntity.Vnc?.userName != null)
            {
                env.Add("USER", TemplateEntity.Vnc.userName);
            }

            var tr = new TemplateResource
            {
                ApiVersion = "hackathon.kaiyuanshe.cn/v1",
                Kind = "Template",
                Metadata = new k8s.Models.V1ObjectMeta
                {
                    Name = $"template-{TemplateEntity.HackathonName}-{TemplateEntity.Name}",
                    NamespaceProperty = "default",
                    Labels = new Dictionary<string, string>
                    {
                        { "hackathonName", TemplateEntity.HackathonName },
                        { "templateName", TemplateEntity.Name },
                    },
                },
                Data = new TemplateData
                {
                    IngressPort = TemplateEntity.IngressPort,
                    IngressProtocol = TemplateEntity.IngressProtocol.ToString(),
                    Type = "Pod",
                    PodTemplate = new PodTemplate
                    {
                        Image = TemplateEntity.Image,
                        EnvironmentVariables = env,
                        Command = TemplateEntity.Commands,
                    },
                    VncConnection = TemplateEntity.Vnc == null ? null : new VncConnection
                    {
                        Username = TemplateEntity.Vnc.userName,
                        Password = TemplateEntity.Vnc.password,
                    },
                },
            };

            return tr;
        }
    }
}
