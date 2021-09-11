using k8s;
using Kaiyuanshe.OpenHackathon.Server.K8S;
using Kaiyuanshe.OpenHackathon.Server.K8S.Models;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.Extensions.Logging;
using Moq;
using NUnit.Framework;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.ServerTests.K8S
{
    class KubernetesClusterTests
    {
        [Test]
        public async Task CreateOrUpdateTemplateAsync()
        {
            var logger = new Mock<ILogger<KubernetesCluster>>();
            var k8sconfig = new KubernetesClientConfiguration();
            var kubernetes = new Mock<IKubernetes>();
            kubernetes.Setup(k => k.CreateNamespacedCustomObjectWithHttpMessagesAsync(
                It.IsAny<TemplateResource>(),
                "hackathon.kaiyuanshe.cn", "v1", "default", "templates",
                null, null, null, null, default))
                .ReturnsAsync(new Microsoft.Rest.HttpOperationResponse<object>
                {
                    Response = new System.Net.Http.HttpResponseMessage
                    {
                        StatusCode = System.Net.HttpStatusCode.OK,
                        ReasonPhrase = ""
                    }
                });
            var context = new TemplateContext
            {
                TemplateEntity = new TemplateEntity { }
            };

            var kubernetesCluster = new Mock<KubernetesCluster>(k8sconfig, logger.Object)
            {
                CallBase = true,
            };
            kubernetesCluster.Setup(k => k.GetKubernetes()).Returns(kubernetes.Object);

            await kubernetesCluster.Object.CreateOrUpdateTemplateAsync(context, default);
        }
    }
}
