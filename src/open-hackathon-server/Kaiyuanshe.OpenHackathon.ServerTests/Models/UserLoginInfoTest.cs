using NUnit.Framework;
using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Text;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Models
{
    [TestFixture]
    public class UserLoginInfoTest
    {
        [TestCase(null, true)]
        [TestCase("", false)]
        [TestCase("13012345678", true)]
        [TestCase("86 13012345678", true)]
        [TestCase("+86 13012345678", true)]
        [TestCase("02112345678", true)]
        [TestCase("021-12345678", true)]
        [TestCase("86-21-12345678", true)]
        [TestCase("+86-21-12345678", true)]
        public void PhoneAttributeTest(string phone, bool isValid)
        {
            var phoneAttr = new PhoneAttribute();
            Assert.AreEqual(isValid, phoneAttr.IsValid(phone));
        }
    }
}
