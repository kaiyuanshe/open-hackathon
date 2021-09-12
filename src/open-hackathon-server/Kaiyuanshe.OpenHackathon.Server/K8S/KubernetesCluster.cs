using k8s;
using Kaiyuanshe.OpenHackathon.Server.K8S.Models;
using Microsoft.Extensions.Logging;
using Microsoft.Rest;
using Microsoft.Rest.Serialization;
using Newtonsoft.Json;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.K8S
{
    public interface IKubernetesCluster
    {
        Task CreateOrUpdateTemplateAsync(TemplateContext context, CancellationToken cancellationToken);
        Task<TemplateResource> GetTemplateAsync(TemplateContext context, CancellationToken cancellationToken);
    }

    public class KubernetesCluster : IKubernetesCluster
    {
        IKubernetes kubeClient;
        private readonly ILogger logger;

        public KubernetesCluster(
            IKubernetes kubernetes,
            ILogger logger)
        {
            kubeClient = kubernetes;
            this.logger = logger;
        }

        public async Task CreateOrUpdateTemplateAsync(TemplateContext context, CancellationToken cancellationToken)
        {
            var cr = await GetTemplateAsync(context, cancellationToken);
            if (cr == null)
            {
                if (context.Status.Code != 404)
                {
                    return;
                }

                // create if not found
                var customResource = context.BuildCustomResource();
                try
                {
                    var resp = await kubeClient.CreateNamespacedCustomObjectWithHttpMessagesAsync(
                        customResource,
                        TemplateResource.Group,
                        TemplateResource.Version,
                        customResource.Metadata.NamespaceProperty ?? "default",
                        TemplateResource.Plural);
                    logger.TraceInformation($"CreateTemplateAsync. Status: {resp.Response.StatusCode}, reason: {resp.Response.Content.AsString()}");
                    context.Status = new k8s.Models.V1Status
                    {
                        Code = (int)resp.Response.StatusCode,
                        Reason = resp.Response.ReasonPhrase,
                    };
                }
                catch (HttpOperationException exception)
                {
                    if (exception.Response?.Content == null)
                        throw;

                    context.Status = JsonConvert.DeserializeObject<k8s.Models.V1Status>(exception.Response.Content);
                }
            }
            else
            {
                // Patch
            }
        }

        public async Task<TemplateResource> GetTemplateAsync(TemplateContext context, CancellationToken cancellationToken)
        {
            try
            {
                var cr = await kubeClient.GetNamespacedCustomObjectWithHttpMessagesAsync(
                    TemplateResource.Group,
                    TemplateResource.Version,
                    context.GetNamespace(),
                    TemplateResource.Plural,
                    context.GetTemplateResourceName(),
                    null,
                    cancellationToken);
                context.Status = new k8s.Models.V1Status
                {
                    Code = 200,
                    Status = "success",
                };
                return SafeJsonConvert.DeserializeObject<TemplateResource>(cr.Body.ToString());
            }
            catch (HttpOperationException exception)
            {
                if (exception.Response?.Content == null)
                    throw;

                logger.TraceInformation(exception.Response.Content);
                context.Status = JsonConvert.DeserializeObject<k8s.Models.V1Status>(exception.Response.Content);
                return null;
            }
        }
    }
}
