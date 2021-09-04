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
        Task<TemplateEntity> CreateTemplateAsync(Template template, CancellationToken cancellationToken);
    }

    public class ExperimentManagement : ManagementClientBase, IExperimentManagement
    {
        private readonly ILogger logger;

        public ExperimentManagement(ILogger<ExperimentManagement> logger)
        {
            this.logger = logger;
        }

        #region CreateTemplateAsync
        public async Task<TemplateEntity> CreateTemplateAsync(Template template, CancellationToken cancellationToken)
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
                UserName = template.userName,
            };
            await StorageContext.TemplateTable.InsertOrMergeAsync(entity, cancellationToken);

            // TODO: call K8S API.

            return entity;
        }
        #endregion
    }
}
