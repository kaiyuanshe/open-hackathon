using k8s;
using k8s.KubeConfigModels;
using Kaiyuanshe.OpenHackathon.Server.Storage;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.K8S
{
    public interface IKubernetesConfigProvider
    {
        Task<KubernetesClientConfiguration> GetDefaultConfigAsync(CancellationToken cancellationToken);
    }

    public class KubernetesConfigProvider : IKubernetesConfigProvider
    {
        static readonly string DefaultConfigBlob = "default/kubeconfig.yaml";
        public IStorageContext StorageContext { get; set; }

        public async Task<KubernetesClientConfiguration> GetDefaultConfigAsync(CancellationToken cancellationToken)
        {
            var configObject = await GetDefaultConfigObjectAsync(cancellationToken);
            return KubernetesClientConfiguration.BuildConfigFromConfigObject(configObject);
        }

        internal async Task<K8SConfiguration> GetDefaultConfigObjectAsync(CancellationToken cancellationToken)
        {
            var content = await StorageContext.KubernetesBlobContainer.DownloadBlockBlobAsync(DefaultConfigBlob, cancellationToken);
            return Yaml.LoadFromString<K8SConfiguration>(content);
        }
    }
}
