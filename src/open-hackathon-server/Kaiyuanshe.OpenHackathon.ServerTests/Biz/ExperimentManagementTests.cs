using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Storage;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Kaiyuanshe.OpenHackathon.Server.Storage.Tables;
using Microsoft.Extensions.Logging;
using Moq;
using NUnit.Framework;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Biz
{
    class ExperimentManagementTests
    {
        [Test]
        public async Task CreateTemplateAsync()
        {
            Template template = new Template
            {
                hackathonName = "hack",
                name = "default",
                commands = new string[] { "a", "b", "c" },
                environmentVariables = new Dictionary<string, string>
                {
                    { "e1", "v1" },
                    { "e2", "v2" }
                },
                image = "image",
                ingressPort = 22,
                ingressProtocol = IngressProtocol.vnc,
                vnc = new Vnc { userName = "un", password = "pw" },
            };

            var logger = new Mock<ILogger<ExperimentManagement>>();

            var templateTable = new Mock<ITemplateTable>();
            templateTable.Setup(p => p.InsertOrMergeAsync(It.Is<TemplateEntity>(t =>
                t.PartitionKey == "hack" &&
                t.RowKey == "default" &&
                t.Commands.Length == 3 &&
                t.Commands[1] == "b" &&
                t.EnvironmentVariables.Count == 2 &&
                t.EnvironmentVariables.Last().Value == "v2" &&
                t.Image == "image" &&
                t.IngressPort == 22 &&
                t.IngressProtocol == IngressProtocol.vnc &&
                t.Vnc.userName == "un" &&
                t.Vnc.password == "pw"), default));
            var storageContext = new Mock<IStorageContext>();
            storageContext.SetupGet(p => p.TemplateTable).Returns(templateTable.Object);

            var management = new ExperimentManagement(logger.Object)
            {
                StorageContext = storageContext.Object,
            };
            var result = await management.CreateTemplateAsync(template, default);

            Mock.VerifyAll(storageContext, templateTable);
            storageContext.VerifyAll();
            templateTable.VerifyAll();

            Assert.AreEqual("hack", result.PartitionKey);
            Assert.AreEqual("default", result.RowKey);
            Assert.AreEqual(22, result.IngressPort);
            Assert.AreEqual("un", result.Vnc.userName);
        }
    }
}
