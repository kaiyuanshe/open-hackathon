using k8s;
using Kaiyuanshe.OpenHackathon.Server.K8S.Models;
using Microsoft.Extensions.Logging;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.K8S
{
    public interface IKubernetesCluster
    {
        Task CreateTemplateAsync(TemplateResource templateResource, CancellationToken cancellationToken);
    }

    public class KubernetesCluster : IKubernetesCluster
    {
        KubernetesClientConfiguration kubeconfig;
        private readonly ILogger logger;

        public KubernetesCluster(
            KubernetesClientConfiguration kubernetesClientConfiguration,
            ILoggerFactory loggerFactory)
        {
            kubeconfig = kubernetesClientConfiguration;
            logger = loggerFactory.CreateLogger<KubernetesCluster>();
        }

        public async Task CreateTemplateAsync(TemplateResource templateResource, CancellationToken cancellationToken)
        {
            var kubernetes = GetKubernetes();
            var resp = await kubernetes.CreateNamespacedCustomObjectWithHttpMessagesAsync(
                templateResource,
                TemplateResource.Group,
                TemplateResource.Version,
                templateResource.Metadata.NamespaceProperty ?? "default",
                TemplateResource.Plural);
            logger.LogInformation($"CreateTemplateAsync. Status: {resp.Response.StatusCode}, reason: {resp.Response.ReasonPhrase}");
        }

        internal virtual Kubernetes GetKubernetes()
        {
            return new Kubernetes(kubeconfig);
        }

        internal virtual GenericClient GetGenericClient(string group, string version, string plural)
        {
            return new GenericClient(kubeconfig, group, version, plural);
        }
    }
}
