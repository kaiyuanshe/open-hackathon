using k8s;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.K8S
{
    public interface IKubernetesCluster
    {
        Task CreateTemplateAsync(TemplateContext templateContext, CancellationToken cancellationToken);
    }

    public class KubernetesCluster : IKubernetesCluster
    {
        KubernetesClientConfiguration kubeconfig;

        public KubernetesCluster(KubernetesClientConfiguration kubernetesClientConfiguration)
        {
            kubeconfig = kubernetesClientConfiguration;
        }

        public async Task CreateTemplateAsync(TemplateContext templateContext, CancellationToken cancellationToken)
        {
            // var kubernetes = await KubernetesClusterFactory.GetDefaultKubernetes(cancellationToken);
            //GenericClient client = new GenericClient();
            //kubernetes.listnamespacedcu
        }
    }
}
