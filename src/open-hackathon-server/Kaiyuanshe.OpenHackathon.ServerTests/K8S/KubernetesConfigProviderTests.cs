using k8s;
using Kaiyuanshe.OpenHackathon.Server.K8S;
using Kaiyuanshe.OpenHackathon.Server.Storage;
using Kaiyuanshe.OpenHackathon.Server.Storage.BlobContainers;
using Microsoft.Rest;
using Moq;
using NUnit.Framework;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.ServerTests.K8S
{
    class KubernetesConfigProviderTests
    {
        #region GetDefaultConfigObjectAsync
        [Test]
        public async Task GetDefaultConfigObjectAsync()
        {
            string testConfig = @"
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: certificate-authority-data
    server: https://10.0.0.1:8443
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
    client-certificate-data: client-certificate-data 
    client-key-data: client-key-data
";

            var kubeContainer = new Mock<IKubernetesBlobContainer>();
            kubeContainer.Setup(k => k.DownloadBlockBlobAsync("default/kubeconfig.yaml", default)).ReturnsAsync(testConfig);
            var storage = new Mock<IStorageContext>();
            storage.SetupGet(s => s.KubernetesBlobContainer).Returns(kubeContainer.Object);

            var kubeConfigProvider = new KubernetesConfigProvider
            {
                StorageContext = storage.Object,
            };
            var config = await kubeConfigProvider.GetDefaultConfigObjectAsync(default);

            Assert.AreEqual("v1", config.ApiVersion);
            Assert.AreEqual("certificate-authority-data", config.Clusters.Single().ClusterEndpoint.CertificateAuthorityData);
            Assert.AreEqual("https://10.0.0.1:8443", config.Clusters.Single().ClusterEndpoint.Server);
            Assert.AreEqual("kubernetes", config.Clusters.Single().Name);
            Assert.AreEqual("kubernetes", config.Contexts.Single().ContextDetails.Cluster);
            Assert.AreEqual("kubernetes-admin", config.Contexts.Single().ContextDetails.User);
            Assert.AreEqual("kubernetes-admin@kubernetes", config.Contexts.Single().Name);
            Assert.AreEqual("kubernetes-admin@kubernetes", config.CurrentContext);
            Assert.AreEqual("Config", config.Kind);
            Assert.AreEqual(0, config.Preferences.Count);
            Assert.AreEqual("kubernetes-admin", config.Users.First().Name);
            Assert.AreEqual("client-certificate-data", config.Users.First().UserCredentials.ClientCertificateData);
            Assert.AreEqual("client-key-data", config.Users.First().UserCredentials.ClientKeyData);
        }
        #endregion

        #region GetDefaultConfigAsync
        [Test]
        public async Task GetDefaultConfigAsync()
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
            var kubeContainer = new Mock<IKubernetesBlobContainer>();
            kubeContainer.Setup(k => k.DownloadBlockBlobAsync("default/kubeconfig.yaml", default)).ReturnsAsync(testConfig);
            var storage = new Mock<IStorageContext>();
            storage.SetupGet(s => s.KubernetesBlobContainer).Returns(kubeContainer.Object);

            var kubeConfigProvider = new KubernetesConfigProvider
            {
                StorageContext = storage.Object,
            };

            var config = await kubeConfigProvider.GetDefaultConfigAsync(default);
            var cluster = new Kubernetes(config);

            Assert.AreEqual("https://10.0.0.1:8443/", cluster.BaseUri.AbsoluteUri);
            var credential = (BasicAuthenticationCredentials)cluster.Credentials;
            Assert.AreEqual("username", credential.UserName);
            Assert.AreEqual("password", credential.Password);
        }
        #endregion
    }
}
