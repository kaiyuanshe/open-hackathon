using k8s.Models;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.AspNetCore.JsonPatch;
using System.Collections.Generic;

namespace Kaiyuanshe.OpenHackathon.Server.K8S.Models
{
    public class TemplateContext
    {
        public TemplateEntity TemplateEntity { get; set; }
        public V1Status Status { get; set; }

        public string GetTemplateResourceName()
        {
            return $"{TemplateEntity.HackathonName}-{TemplateEntity.Name}";
        }

        public string GetNamespace()
        {
            return "default";
        }

        public IDictionary<string, string> BuildEnvironmentVariables()
        {
            var env = TemplateEntity.EnvironmentVariables == null ?
                new Dictionary<string, string>() :
                new Dictionary<string, string>(TemplateEntity.EnvironmentVariables);

            if (TemplateEntity.Vnc?.userName != null)
            {
                env.Add("USER", TemplateEntity.Vnc.userName);
            }
            return env;
        }

        public TemplateResource BuildCustomResource()
        {
            var tr = new TemplateResource
            {
                ApiVersion = "hackathon.kaiyuanshe.cn/v1",
                Kind = "Template",
                Metadata = new k8s.Models.V1ObjectMeta
                {
                    Name = GetTemplateResourceName(),
                    NamespaceProperty = GetNamespace(),
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
                        EnvironmentVariables = BuildEnvironmentVariables(),
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

        public V1Patch BuildPatch()
        {
            var jsonPatch = new JsonPatchDocument<TemplateResource>();

            jsonPatch.Replace(t => t.Data.IngressPort, TemplateEntity.IngressPort);
            jsonPatch.Replace(t => t.Data.IngressProtocol, TemplateEntity.IngressProtocol.ToString());
            jsonPatch.Replace(t => t.Data.PodTemplate.Image, TemplateEntity.Image);
            jsonPatch.Replace(t => t.Data.PodTemplate.EnvironmentVariables, BuildEnvironmentVariables());
            jsonPatch.Replace(t => t.Data.PodTemplate.Command, TemplateEntity.Commands);

            if (TemplateEntity.Vnc != null)
            {
                jsonPatch.Replace(t => t.Data.VncConnection.Username, TemplateEntity.Vnc.userName);
                jsonPatch.Replace(t => t.Data.VncConnection.Password, TemplateEntity.Vnc.password);
            }

            var patch = new V1Patch(jsonPatch, V1Patch.PatchType.JsonPatch);
            return patch;
        }
    }
}
