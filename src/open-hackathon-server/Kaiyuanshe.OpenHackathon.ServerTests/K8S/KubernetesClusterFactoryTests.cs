using k8s;
using k8s.KubeConfigModels;
using Kaiyuanshe.OpenHackathon.Server.K8S;
using Microsoft.Rest;
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
            var config = Yaml.LoadFromString<K8SConfiguration>(testConfig);

            var configProvider = new Mock<IKubernetesConfigProvider>();
            configProvider.Setup(p => p.GetDefaultConfigAsync(default)).ReturnsAsync(config);

            var factory = new KubernetesClusterFactory
            {
                KubernetesConfigProvider = configProvider.Object,
            };
            var cluster = await factory.GetDefaultKubernetes(default);

            Assert.AreEqual("https://10.0.0.1:8443/", cluster.BaseUri.AbsoluteUri);
            var credential = (BasicAuthenticationCredentials)cluster.Credentials;
            Assert.AreEqual("username", credential.UserName);
            Assert.AreEqual("password", credential.Password);
        }
    }
}
