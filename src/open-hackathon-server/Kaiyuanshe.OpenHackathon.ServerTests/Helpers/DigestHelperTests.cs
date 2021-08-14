using Kaiyuanshe.OpenHackathon.Server;
using NUnit.Framework;
using System.Text;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Helpers
{
    [TestFixture]
    public class DigestHelperTests
    {
        [Test]
        public void SHA512DigestTest()
        {
            string original = "whatever";
            string expected = "ae3d347982977b422948b64011ac14ac76c9ab15898fb562a66a136733aa645fb3a9ccd9bee00cc578c2f44f486af47eb254af7c174244086d174cc52341e63a";
            System.Console.WriteLine(DigestHelper.SHA512Digest(original));
            Assert.AreEqual(expected, DigestHelper.SHA512Digest(Encoding.UTF8.GetBytes(original)));
            Assert.AreEqual(expected, DigestHelper.SHA512Digest(original));
        }

        [TestCase("a", "b975c10c-f1c0-a8b6-31c3-99e269772661")]
        [TestCase("whatever", "26598c00-86ca-2310-c1d2-a36653fd88e2")]
        public void String2Guid(string input, string expectedGuid)
        {
            var guid = DigestHelper.String2Guid(input);
            Assert.AreEqual(expectedGuid, guid.ToString());
        }
    }
}