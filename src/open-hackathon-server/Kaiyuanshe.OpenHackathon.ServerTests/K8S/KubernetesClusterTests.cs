using k8s;
using k8s.Models;
using Kaiyuanshe.OpenHackathon.Server.K8S;
using Kaiyuanshe.OpenHackathon.Server.K8S.Models;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.Extensions.Logging;
using Microsoft.Rest;
using Moq;
using NUnit.Framework;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.ServerTests.K8S
{
    class KubernetesClusterTests
    {
        #region CreateOrUpdateTemplateAsync
        [Test]
        public async Task CreateOrUpdateTemplateAsync_OtherError()
        {
            var logger = new Mock<ILogger<KubernetesCluster>>();

            string content = "{\"code\": 422}";
            var kubernetes = new Mock<IKubernetes>();
            kubernetes.Setup(k => k.GetNamespacedCustomObjectWithHttpMessagesAsync(
               "hackathon.kaiyuanshe.cn", "v1", "default", "templates",
               "pk-rk",
               null, default))
               .Throws(new HttpOperationException
               {
                   Response = new HttpResponseMessageWrapper(new System.Net.Http.HttpResponseMessage(), content)
               });
            var context = new TemplateContext
            {
                TemplateEntity = new TemplateEntity { PartitionKey = "pk", RowKey = "rk" }
            };

            var kubernetesCluster = new KubernetesCluster(kubernetes.Object, logger.Object);
            await kubernetesCluster.CreateOrUpdateTemplateAsync(context, default);

            Mock.VerifyAll(kubernetes);
            kubernetes.VerifyNoOtherCalls();
        }

        [Test]
        public async Task CreateOrUpdateTemplateAsync_Create()
        {
            var logger = new Mock<ILogger<KubernetesCluster>>();

            string content = "{\"code\": 404}";
            var kubernetes = new Mock<IKubernetes>();
            kubernetes.Setup(k => k.GetNamespacedCustomObjectWithHttpMessagesAsync(
               "hackathon.kaiyuanshe.cn", "v1", "default", "templates",
               "pk-rk",
               null, default))
               .Throws(new HttpOperationException
               {
                   Response = new HttpResponseMessageWrapper(new System.Net.Http.HttpResponseMessage(), content)
               });
            kubernetes.Setup(k => k.CreateNamespacedCustomObjectWithHttpMessagesAsync(
                It.IsAny<TemplateResource>(),
                "hackathon.kaiyuanshe.cn", "v1", "default", "templates",
                null, null, null, null, default))
               .ReturnsAsync(new HttpOperationResponse<object>
               {
                   Response = new System.Net.Http.HttpResponseMessage
                   {
                       StatusCode = System.Net.HttpStatusCode.Created,
                       ReasonPhrase = "success"
                   },
               });
            var context = new TemplateContext
            {
                TemplateEntity = new TemplateEntity { PartitionKey = "pk", RowKey = "rk" }
            };

            var kubernetesCluster = new KubernetesCluster(kubernetes.Object, logger.Object);
            await kubernetesCluster.CreateOrUpdateTemplateAsync(context, default);

            Mock.VerifyAll(kubernetes);
            kubernetes.VerifyNoOtherCalls();

            Assert.AreEqual(201, context.Status.Code);
            Assert.AreEqual("success", context.Status.Reason);
        }

        [Test]
        public async Task CreateOrUpdateTemplateAsync_Patch()
        {
            var logger = new Mock<ILogger<KubernetesCluster>>();
            var kubernetes = new Mock<IKubernetes>();
            kubernetes.Setup(k => k.GetNamespacedCustomObjectWithHttpMessagesAsync(
                "hackathon.kaiyuanshe.cn", "v1", "default", "templates",
                "pk-rk",
                null, default))
                .ReturnsAsync(new Microsoft.Rest.HttpOperationResponse<object>
                {
                    Body = "{\"kind\":\"template\"}"
                });
            kubernetes.Setup(k => k.PatchNamespacedCustomObjectWithHttpMessagesAsync(
                It.IsAny<V1Patch>(),
                "hackathon.kaiyuanshe.cn", "v1", "default", "templates",
                "pk-rk",
                null, null, null, null, default))
                .ReturnsAsync(new HttpOperationResponse<object>
                {
                    Response = new System.Net.Http.HttpResponseMessage
                    {
                        StatusCode = System.Net.HttpStatusCode.OK,
                        ReasonPhrase = "success",
                    },
                });
            var context = new TemplateContext
            {
                TemplateEntity = new TemplateEntity { PartitionKey = "pk", RowKey = "rk" }
            };

            var kubernetesCluster = new KubernetesCluster(kubernetes.Object, logger.Object);
            await kubernetesCluster.CreateOrUpdateTemplateAsync(context, default);

            Mock.VerifyAll(kubernetes);
            kubernetes.VerifyNoOtherCalls();

            Assert.AreEqual(200, context.Status.Code);
            Assert.AreEqual("success", context.Status.Reason);
        }
        #endregion

        #region GetTemplateAsync
        [Test]
        public async Task GetTemplateAsync()
        {
            var logger = new Mock<ILogger<KubernetesCluster>>();
            var kubernetes = new Mock<IKubernetes>();
            kubernetes.Setup(k => k.GetNamespacedCustomObjectWithHttpMessagesAsync(
                "hackathon.kaiyuanshe.cn", "v1", "default", "templates",
                "pk-rk",
                null, default))
                .ReturnsAsync(new Microsoft.Rest.HttpOperationResponse<object>
                {
                    Body = "{\"kind\":\"template\"}"
                });
            var context = new TemplateContext
            {
                TemplateEntity = new TemplateEntity { PartitionKey = "pk", RowKey = "rk" }
            };

            var kubernetesCluster = new KubernetesCluster(kubernetes.Object, logger.Object);
            var result = await kubernetesCluster.GetTemplateAsync(context, default);

            Mock.VerifyAll(kubernetes);
            kubernetes.VerifyNoOtherCalls();

            Assert.AreEqual("template", result.Kind);
            Assert.AreEqual(200, context.Status.Code);
            Assert.AreEqual("success", context.Status.Status);
        }
        #endregion

        #region UpdateTemplateAsync
        [Test]
        public async Task UpdateTemplateAsync()
        {
            var logger = new Mock<ILogger<KubernetesCluster>>();
            var kubernetes = new Mock<IKubernetes>();
            kubernetes.Setup(k => k.PatchNamespacedCustomObjectWithHttpMessagesAsync(
                It.IsAny<V1Patch>(),
                "hackathon.kaiyuanshe.cn", "v1", "default", "templates",
                "pk-rk",
                null, null, null, null, default))
                .ReturnsAsync(new HttpOperationResponse<object>
                {
                    Response = new System.Net.Http.HttpResponseMessage
                    {
                        StatusCode = System.Net.HttpStatusCode.OK,
                        ReasonPhrase = "success",
                    },
                });
            var context = new TemplateContext
            {
                TemplateEntity = new TemplateEntity { PartitionKey = "pk", RowKey = "rk" }
            };

            var kubernetesCluster = new KubernetesCluster(kubernetes.Object, logger.Object);
            await kubernetesCluster.UpdateTemplateAsync(context, default);

            Mock.VerifyAll(kubernetes);
            kubernetes.VerifyNoOtherCalls();

            Assert.AreEqual(200, context.Status.Code);
            Assert.AreEqual("success", context.Status.Reason);
        }
        #endregion
    }
}
