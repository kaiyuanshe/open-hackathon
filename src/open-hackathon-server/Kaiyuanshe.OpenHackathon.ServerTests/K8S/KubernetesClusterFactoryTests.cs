using k8s;
using k8s.KubeConfigModels;
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
            string testConfig = @"
apiVersion: v1
clusters:
- cluster:
    server: https://10.0.0.1:8443
    insecure-skip-tls-verify: true
  name: kubernetes
contexts:
- context:
    cluster: kubernetes
    user: kubernetes-admin
  name: kubernetes-admin@kubernetes
current-context: kubernetes-admin@kubernetes
kind: Config
preferences: {}
users:
- name: kubernetes-admin
  user:
    password: password
    username: username
";
            var configObj = Yaml.LoadFromString<K8SConfiguration>(testConfig);
            KubernetesClientConfiguration kubeconfig = KubernetesClientConfiguration.BuildConfigFromConfigObject(configObj);

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
