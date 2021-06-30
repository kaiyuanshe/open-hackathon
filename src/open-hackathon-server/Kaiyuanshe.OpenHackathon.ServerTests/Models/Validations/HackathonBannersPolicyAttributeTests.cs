using NUnit.Framework;
using System.Collections.Generic;
using Kaiyuanshe.OpenHackathon.Server.Models.Validations;
using Kaiyuanshe.OpenHackathon.Server.Models;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Models.Validations.Tests
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
                yield return new TestCaseData(new PictureInfo[] { }, false);
                yield return new TestCaseData(new PictureInfo[] {
                    new PictureInfo{ uri= "https://foo.com/bar.jpg" }
                }, true);

                List<PictureInfo> images = new List<PictureInfo>();
                for (int i = 0; i < HackathonBannersPolicyAttribute.MaxBannerCount; i++)
                {
                    images.Add(new PictureInfo { uri = $"http://foo.com/bar{i}.jpg" });
                }
                yield return new TestCaseData(images.ToArray(), true);

                // too many
                images.Add(new PictureInfo { uri = "https://foo.com/barx.jpg" });
                yield return new TestCaseData(images.ToArray(), false);
            }
        }

        [Test, TestCaseSource(nameof(PolicyTestCaseData))]
        public void IsValidTest(PictureInfo[] banners, bool valid)
        {
            var attribute = new HackathonBannersPolicyAttribute();
            Assert.AreEqual(valid, attribute.IsValid(banners));
        }
    }
}