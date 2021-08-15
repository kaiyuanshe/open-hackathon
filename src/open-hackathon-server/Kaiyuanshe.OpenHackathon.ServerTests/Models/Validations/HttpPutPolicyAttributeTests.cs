using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Models.Validations;
using NUnit.Framework;
using System.Collections;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Models.Validations
{
    public class HttpPutPolicyAttributeTests
    {
        private static IEnumerable IsValidTestData()
        {
            // arg0: value
            // arg1: isValid
            // arg2: members

            yield return new TestCaseData(
                null,
                true,
                null);

            yield return new TestCaseData(
                new Rating(),
                false,
                new List<string> { "teamId", "ratingKindId", "score" });

            yield return new TestCaseData(
                new Rating { teamId = "tid", score = 5 },
                false,
                new List<string> { "ratingKindId" });
        }

        [Test, TestCaseSource(nameof(IsValidTestData))]
        public void IsValidTest(Rating value, bool isValid, List<string> missingMembers)
        {
            var attr = new HttpPutPolicyAttribute();
            Assert.AreEqual(isValid, attr.IsValid(value));

            if (value != null && missingMembers != null)
            {
                var context = new ValidationContext(value);
                var result = attr.GetValidationResult(value, context);
                Assert.AreEqual(missingMembers.Count(), result.MemberNames.Count());
                Assert.AreEqual(missingMembers.Count(), missingMembers.Intersect(result.MemberNames).Count());
            }
        }
    }
}
