using k8s;
using Kaiyuanshe.OpenHackathon.Server.K8S;
using Microsoft.Extensions.Logging;
using Moq;
using NUnit.Framework;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.ServerTests.K8S
{
    class KubernetesClusterFactoryTests
    {
        [Test]
        public async Task GetDefaultKubernetes()
        {
            KubernetesClientConfiguration kubeconfig = new KubernetesClientConfiguration();

            var configProvider = new Mock<IKubernetesConfigProvider>();
            configProvider.Setup(p => p.GetDefaultConfigAsync(default)).ReturnsAsync(kubeconfig);

            var factory = new KubernetesClusterFactory
            {
                KubernetesConfigProvider = configProvider.Object,
                LoggerFactory = new Mock<ILoggerFactory>().Object,
            };
            var cluster = await factory.GetDefaultKubernetes(default);
            Assert.AreEqual(typeof(KubernetesCluster), cluster.GetType());

            var cluster2 = await factory.GetDefaultKubernetes(default);
            Assert.AreEqual(typeof(KubernetesCluster), cluster2.GetType());
            Assert.AreSame(cluster, cluster2);

            configProvider.Verify(p => p.GetDefaultConfigAsync(default), Times.Once);
            configProvider.VerifyNoOtherCalls();
        }
    }
}
