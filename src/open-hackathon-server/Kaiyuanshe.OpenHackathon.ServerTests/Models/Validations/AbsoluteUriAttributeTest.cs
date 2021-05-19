using Kaiyuanshe.OpenHackathon.Server.Models.Validations;
using NUnit.Framework;
using System;
using System.Collections.Generic;
using System.Text;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Models.Validations
{
    [TestFixture]
    public class AbsoluteUriAttributeTest
    {
        [Test]
        public void IsValidTest()
        {
            var attribute = new AbsoluteUriAttribute();
            Assert.AreEqual(true, attribute.IsValid(null));
            Assert.AreEqual(false, attribute.IsValid("foo"));
            Assert.AreEqual(true, attribute.IsValid("http://a.com/b.png"));
            Assert.AreEqual(true, attribute.IsValid("https://a.com/b.png"));
            Assert.AreEqual(false, attribute.IsValid("ftp://a.com/b.png"));
        }
    }
}
