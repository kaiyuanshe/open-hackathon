using Kaiyuanshe.OpenHackathon.Server.K8S.Models;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using NUnit.Framework;
using System.Collections.Generic;

namespace Kaiyuanshe.OpenHackathon.ServerTests.K8S
{
    class TemplateContextTests
    {
        [Test]
        public void BuildCustomResource()
        {
            var context = new TemplateContext
            {
                TemplateEntity = new TemplateEntity
                {
                    PartitionKey = "pk",
                    RowKey = "rk",
                    IngressPort = 5901,
                    IngressProtocol = Server.Models.IngressProtocol.vnc,
                    Image = "image",
                    EnvironmentVariables = new Dictionary<string, string>
                    {
                        { "key", "value" }
                    },
                    Commands = new string[] { "a" },
                    Vnc = new Vnc
                    {
                        userName = "un",
                        password = "pwd"
                    },
                }
            };

            var cr = context.BuildCustomResource();
            Assert.AreEqual("hackathon.kaiyuanshe.cn/v1", cr.ApiVersion);
            Assert.AreEqual("Template", cr.Kind);
            Assert.AreEqual("pk-rk", cr.Metadata.Name);
            Assert.AreEqual("default", cr.Metadata.NamespaceProperty);
            Assert.AreEqual(2, cr.Metadata.Labels.Count);
            Assert.AreEqual("pk", cr.Metadata.Labels["hackathonName"]);
            Assert.AreEqual("rk", cr.Metadata.Labels["templateName"]);
            Assert.AreEqual(5901, cr.Data.IngressPort);
            Assert.AreEqual("vnc", cr.Data.IngressProtocol);
            Assert.AreEqual("Pod", cr.Data.Type);
            Assert.AreEqual("image", cr.Data.PodTemplate.Image);
            Assert.AreEqual("a", cr.Data.PodTemplate.Command[0]);
            Assert.AreEqual("value", cr.Data.PodTemplate.EnvironmentVariables["key"]);
            Assert.AreEqual("un", cr.Data.PodTemplate.EnvironmentVariables["USER"]);
            Assert.AreEqual("un", cr.Data.VncConnection.Username);
            Assert.AreEqual("pwd", cr.Data.VncConnection.Password);
        }
    }
}
