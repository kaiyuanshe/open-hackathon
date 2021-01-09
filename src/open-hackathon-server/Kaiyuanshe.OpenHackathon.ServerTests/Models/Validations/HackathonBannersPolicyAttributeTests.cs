using NUnit.Framework;
using System.Collections.Generic;

namespace Kaiyuanshe.OpenHackathon.Server.Models.Validations.Tests
{
    [TestFixture]
    public class HackathonBannersPolicyAttributeTests
    {
        private static IEnumerable<TestCaseData> PolicyTestCaseData
        {
            get
            {
                yield return new TestCaseData(null, true);
                // at least 1
                yield return new TestCaseData(new string[] { }, false);
                yield return new TestCaseData(new string[] { "https://foo.com/bar.jpg" }, true);
                // invalid uri
                yield return new TestCaseData(new string[] { "invalid uri" }, false);

                List<string> images = new List<string>();
                for (int i = 0; i < HackathonBannersPolicyAttribute.MaxBannerCount; i++)
                {
                    images.Add($"http://foo.com/bar{i}.jpg");
                }
                yield return new TestCaseData(images.ToArray(), true);

                // too many
                images.Add("https://foo.com/barx.jpg");
                yield return new TestCaseData(images.ToArray(), false);
            }
        }

        [Test, TestCaseSource(nameof(PolicyTestCaseData))]
        public void IsValidTest(string[] banners, bool valid)
        {
            var attribute = new HackathonBannersPolicyAttribute();
            Assert.AreEqual(valid, attribute.IsValid(banners));
        }
    }
}