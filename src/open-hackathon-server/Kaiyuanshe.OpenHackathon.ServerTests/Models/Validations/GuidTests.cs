using Kaiyuanshe.OpenHackathon.Server.Models.Validations;
using NUnit.Framework;
using System;
using System.Collections.Generic;
using System.Text;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Models.Validations
{
    public class GuidTests
    {
        [Test]
        public void IsValidTest()
        {
            var attribute = new GuidAttribute();
            Assert.AreEqual(true, attribute.IsValid(null));
            Assert.AreEqual(false, attribute.IsValid("foo"));
            Assert.AreEqual(true, attribute.IsValid(Guid.Empty));
            Assert.AreEqual(true, attribute.IsValid(Guid.NewGuid()));
            Assert.AreEqual(true, attribute.IsValid("d1e40c38-cc2a-445f-9eab-60c253256c57"));
            Assert.AreEqual(false, attribute.IsValid("d1e40c38-cc2a-445f-9eab-60c253256c5"));
        }
    }
}
