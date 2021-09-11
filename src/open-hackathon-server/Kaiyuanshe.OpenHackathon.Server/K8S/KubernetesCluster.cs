using k8s;
using Kaiyuanshe.OpenHackathon.Server.K8S.Models;
using Microsoft.Extensions.Logging;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.K8S
{
    public interface IKubernetesCluster
    {
        Task CreateOrUpdateTemplateAsync(TemplateContext context, CancellationToken cancellationToken);
    }

    public class KubernetesCluster : IKubernetesCluster
    {
        KubernetesClientConfiguration kubeconfig;
        private readonly ILogger logger;

        public KubernetesCluster(
            KubernetesClientConfiguration kubernetesClientConfiguration,
            ILogger logger)
        {
            kubeconfig = kubernetesClientConfiguration;
            this.logger = logger;
        }

        public async Task CreateOrUpdateTemplateAsync(TemplateContext context, CancellationToken cancellationToken)
        {
            var kubernetes = GetKubernetes();
            var customResource = context.BuildCustomResource();
            var resp = await kubernetes.CreateNamespacedCustomObjectWithHttpMessagesAsync(
                customResource,
                TemplateResource.Group,
                TemplateResource.Version,
                customResource.Metadata.NamespaceProperty ?? "default",
                TemplateResource.Plural);
            logger.TraceInformation($"CreateTemplateAsync. Status: {resp.Response.StatusCode}, reason: {resp.Response.ReasonPhrase}");
        }

        internal virtual IKubernetes GetKubernetes()
        {
            return new Kubernetes(kubeconfig);
        }

        internal virtual GenericClient GetGenericClient(string group, string version, string plural)
        {
            return new GenericClient(kubeconfig, group, version, plural);
        }
    }
}
