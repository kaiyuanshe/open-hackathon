using Kaiyuanshe.OpenHackathon.Server.Storage;
using NUnit.Framework;
using System.Collections;
using System.Collections.Generic;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Helpers
{
    [TestFixture]
    public class TableQueryHelperTests
    {
        private static IEnumerable GetFilters
        {
            get
            {
                yield return new TestCaseData(null, string.Empty);

                yield return new TestCaseData(new List<string>(), string.Empty);

                yield return new TestCaseData(new List<string>
                {
                    "aaa"
                }, "aaa");

                yield return new TestCaseData(new List<string>
                {
                    "ak eq 'av"
                }, "ak eq 'av");

                yield return new TestCaseData(new List<string>
                {
                    "ak eq 'av",
                    ""
                }, "ak eq 'av");

                yield return new TestCaseData(new List<string>
                {
                    "ak eq 'av",
                    "",
                    null,
                    "bk eq 'bv"
                }, "(ak eq 'av) and (bk eq 'bv)");
            }
        }

        //[TestCase(new string[] { }, ExpectedResult = "")]
        //[TestCase("aaa", ExpectedResult = "aaa")]
        //[TestCase("ak eq 'av'", ExpectedResult = "ak eq 'av'")]
        [Test, TestCaseSource(nameof(GetFilters))]
        public void AndTest(List<string> filters, string result)
        {
            Assert.AreEqual(result, TableQueryHelper.And(filters?.ToArray()));
        }
    }
}
