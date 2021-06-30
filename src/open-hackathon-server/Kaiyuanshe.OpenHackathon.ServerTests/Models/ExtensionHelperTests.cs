using Kaiyuanshe.OpenHackathon.Server.Models;
using NUnit.Framework;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Text;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Models
{

    public class ExtensionHelperTests
    {
        private static IEnumerable MergeTestData()
        {
            var e1 = new Extension { name = "e1", value = "v1" };
            var e1c = new Extension { name = "E1", value = "V1" };
            var e2 = new Extension { name = "e2", value = "v2" };
            var e2u = new Extension { name = "e2", value = "v2u" };

            yield return new TestCaseData(
                null,
                new Extension[] { e1, e1 },
                new Extension[] { e1 }
                );

            yield return new TestCaseData(
                new Extension[] { e1, e1 },
                null,
                new Extension[] { e1 }
                );

            yield return new TestCaseData(
                new Extension[] { e1, e1c },
                new Extension[] { e1, e2 },
                new Extension[] { e1c, e1, e2 }
                );

            yield return new TestCaseData(
                new Extension[] { e1, e2 },
                new Extension[] { e1c, e2u },
                new Extension[] { e1, e1c, e2u }
                );
        }

        [Test, TestCaseSource(nameof(MergeTestData))]
        public void Merge(Extension[] extensions, Extension[] updates, Extension[] expectedResult)
        {
            var actual = ExtensionHelper.Merge(extensions, updates);

            Assert.AreEqual(expectedResult.Length, actual.Length);
            for (int i = 0; i < expectedResult.Length; i++)
            {
                Assert.AreEqual(expectedResult[i].name, actual[i].name);
                Assert.AreEqual(expectedResult[i].value, actual[i].value);
            }
        }
    }
}
