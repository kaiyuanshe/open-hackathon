using k8s;
using k8s.KubeConfigModels;
using Kaiyuanshe.OpenHackathon.Server.Storage;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Kubernetes
{
    public interface IKubenetesConfigProvider
    {
        Task<K8SConfiguration> GetDefaultConfigAsync(CancellationToken cancellationToken);
    }

    public class KubenetesConfigProvider : IKubenetesConfigProvider
    {
        static readonly string DefaultConfigBlob = "default/kubeconfig.yaml";
        public IStorageContext StorageContext { get; set; }

        public async Task<K8SConfiguration> GetDefaultConfigAsync(CancellationToken cancellationToken)
        {
            var content = await StorageContext.KubernetesBlobContainer.DownloadBlockBlobAsync(DefaultConfigBlob, cancellationToken);
            return Yaml.LoadFromString<K8SConfiguration>(content);
        }
    }
}
