using k8s;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.K8S
{
    public interface IKubernetesClusterFactory
    {
        Task<Kubernetes> GetDefaultKubernetes(CancellationToken cancellationToken);
    }

    public class KubernetesClusterFactory : IKubernetesClusterFactory
    {
        public IKubernetesConfigProvider KubernetesConfigProvider { get; set; }

        public async Task<Kubernetes> GetDefaultKubernetes(CancellationToken cancellationToken)
        {
            var config = await KubernetesConfigProvider.GetDefaultConfigAsync(cancellationToken);
            var k8sconfig = KubernetesClientConfiguration.BuildConfigFromConfigObject(config);
            return new Kubernetes(k8sconfig);
        }
    }
}
