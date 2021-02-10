using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Controllers;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.ResponseBuilder;
using Kaiyuanshe.OpenHackathon.Server.Storage;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.AspNetCore.Mvc;
using Moq;
using NUnit.Framework;
using System;
using System.Collections.Generic;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Controllers
{
    [TestFixture]
    public class HackathonControllerTest
    {
        [Test]
        public async Task CreateOrUpdateTest_Create()
        {
            var hack = new Hackathon();
            var name = "test1";

            var hackManagerMock = new Mock<IHackathonManagement>();
            hackManagerMock.Setup(p => p.GetHackathonEntityByNameAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
                .ReturnsAsync(default(HackathonEntity));
            hackManagerMock.Setup(p => p.CreateHackathonAsync(hack, It.IsAny<CancellationToken>()))
                .ReturnsAsync(default(HackathonEntity));

            var controller = new HackathonController();
            controller.HackathonManager = hackManagerMock.Object;
            var result = await controller.CreateOrUpdate(name, hack, CancellationToken.None);

            Mock.VerifyAll(hackManagerMock);
            hackManagerMock.Verify(p => p.GetHackathonEntityByNameAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()), Times.Once);
            hackManagerMock.Verify(p => p.CreateHackathonAsync(hack, It.IsAny<CancellationToken>()), Times.Once);
            hackManagerMock.VerifyNoOtherCalls();
            Assert.AreEqual(name, hack.Name);
            Assert.IsTrue(result is OkObjectResult);
        }

        [Test]
        public async Task CreateOrUpdateTest_Update()
        {
            var hack = new Hackathon();
            var entity = new HackathonEntity();
            var name = "test1";

            var hackManagerMock = new Mock<IHackathonManagement>();
            hackManagerMock.Setup(p => p.GetHackathonEntityByNameAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
                .ReturnsAsync(entity);
            hackManagerMock.Setup(p => p.UpdateHackathonAsync(hack, It.IsAny<CancellationToken>()))
                .ReturnsAsync(entity);

            var controller = new HackathonController();
            controller.HackathonManager = hackManagerMock.Object;
            var result = await controller.CreateOrUpdate(name, hack, CancellationToken.None);

            Mock.VerifyAll(hackManagerMock);
            hackManagerMock.Verify(p => p.GetHackathonEntityByNameAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()), Times.Once);
            hackManagerMock.Verify(p => p.UpdateHackathonAsync(hack, It.IsAny<CancellationToken>()), Times.Once);
            hackManagerMock.VerifyNoOtherCalls(); 
            Assert.AreEqual(name, hack.Name);
            Assert.IsTrue(result is OkObjectResult);
        }
    }
}
