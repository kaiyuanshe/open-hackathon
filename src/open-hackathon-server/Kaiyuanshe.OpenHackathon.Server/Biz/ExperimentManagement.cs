using Kaiyuanshe.OpenHackathon.Server.K8S;
using Kaiyuanshe.OpenHackathon.Server.K8S.Models;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.Extensions.Logging;
using System;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Biz
{
    public interface IExperimentManagement
    {
        /// <summary>
        /// Create a template.
        /// </summary>
        Task<TemplateContext> CreateTemplateAsync(Template template, CancellationToken cancellationToken);
    }

    public class ExperimentManagement : ManagementClientBase, IExperimentManagement
    {
        private readonly ILogger logger;

        public IKubernetesClusterFactory KubernetesClusterFactory { get; set; }

        public ExperimentManagement(ILogger<ExperimentManagement> logger)
        {
            this.logger = logger;
        }

        #region CreateTemplateAsync
        public async Task<TemplateContext> CreateTemplateAsync(Template template, CancellationToken cancellationToken)
        {
            if (template == null)
                return null;

            var entity = new TemplateEntity
            {
                PartitionKey = template.hackathonName,
                RowKey = template.name,
                Commands = template.commands,
                CreatedAt = DateTime.UtcNow,
                EnvironmentVariables = template.environmentVariables,
                Image = template.image,
                IngressPort = template.ingressPort,
                IngressProtocol = template.ingressProtocol,
                Vnc = template.vnc,
            };
            await StorageContext.TemplateTable.InsertOrMergeAsync(entity, cancellationToken);

            // call K8S API.
            entity = await StorageContext.TemplateTable.RetrieveAsync(template.hackathonName, template.name, cancellationToken);
            var context = new TemplateContext { TemplateEntity = entity };
            var kubernetesCluster = await KubernetesClusterFactory.GetDefaultKubernetes(cancellationToken);
            await kubernetesCluster.CreateOrUpdateTemplateAsync(context, cancellationToken);

            return context;
        }
        #endregion
    }
}
