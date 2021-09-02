using Kaiyuanshe.OpenHackathon.Server.Models.Validations;
using NUnit.Framework;
using System.Collections.Generic;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Models.Validations
{
    class EnvironmentVariablesAttributeTests
    {
        [Test]
        public void IsValidTest()
        {
            var attribute = new EnvironmentVariablesAttribute();
            Assert.AreEqual(true, attribute.IsValid(null));

            // max number
            Dictionary<string, string> a = new Dictionary<string, string>();
            for (int i = 0; i < 32; i++)
            {
                a[i.ToString()] = i.ToString();
            }
            Assert.AreEqual(true, attribute.IsValid(a));
            a["more"] = "more";
            Assert.AreEqual(false, attribute.IsValid(a));

            // invalid name/value
            Dictionary<string, string> b = new Dictionary<string, string>
            {
                { new string('a', 65), "a"}
            };
            Assert.AreEqual(false, attribute.IsValid(b));

            Dictionary<string, string> c = new Dictionary<string, string>
            {
                {  "a",new string('a', 257)}
            };
            Assert.AreEqual(false, attribute.IsValid(c));
        }
    }
}