using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Models.Validations;
using NUnit.Framework;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Models.Validations
{
    class RemoteConfigPolicyAttributeTests
    {
        [Test]
        public void IsValidTest()
        {
            var attribute = new RemoteConfigPolicyAttribute();
            Assert.AreEqual(true, attribute.IsValid(null));

            // rdp
            Template a = new Template { ingressProtocol = IngressProtocol.rdp };
            Assert.AreEqual(true, attribute.IsValid(a));

            // vnc null
            Template b = new Template { ingressProtocol = IngressProtocol.vnc };
            Assert.AreEqual(false, attribute.IsValid(b));

            // un null
            Template c = new Template
            {
                ingressProtocol = IngressProtocol.vnc,
                vnc = new Vnc
                {
                    password = "pw"
                }
            };
            Assert.AreEqual(false, attribute.IsValid(c));

            // pw null
            Template d = new Template
            {
                ingressProtocol = IngressProtocol.vnc,
                vnc = new Vnc
                {
                    userName = "un"
                }
            };
            Assert.AreEqual(false, attribute.IsValid(d));

            // valid
            Template e = new Template
            {
                ingressProtocol = IngressProtocol.vnc,
                vnc = new Vnc
                {
                    password = "pw",
                    userName = "un"
                }
            };
            Assert.AreEqual(true, attribute.IsValid(e));
        }
    }
}
