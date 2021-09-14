using k8s.Models;
using Kaiyuanshe.OpenHackathon.Server.Models;
using NUnit.Framework;
using System.Collections.Generic;
using System.Linq;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Models
{
    class StatusTests
    {
        [Test]
        public void Convert()
        {
            V1Status v1Status = new V1Status
            {
                Reason = "reason",
                Message = "msg",
                Kind = "status",
                Details = new V1StatusDetails
                {
                    Group = "group",
                    Causes = new List<V1StatusCause>
                    {
                        new V1StatusCause
                        {
                            Field="field"
                        }
                    }
                },
                Status = "success",
                Code = 201
            };

            Status status = Status.FromV1Status(v1Status);
            Assert.AreEqual("reason", status.reason);
            Assert.AreEqual("msg", status.message);
            Assert.AreEqual("status", status.kind);
            Assert.AreEqual("group", status.details.Group);
            Assert.AreEqual("field", status.details.Causes.First().Field);
            Assert.AreEqual("success", status.status);
            Assert.AreEqual(201, status.code);
        }
    }
}
