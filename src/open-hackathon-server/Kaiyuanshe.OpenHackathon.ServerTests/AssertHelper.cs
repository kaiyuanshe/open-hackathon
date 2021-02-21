using Microsoft.AspNetCore.Mvc;
using NUnit.Framework;
using System;
using System.Collections.Generic;
using System.Text;

namespace Kaiyuanshe.OpenHackathon.ServerTests
{
    public static class AssertHelper
    {
        public static void AssertObjectResult(object result, int expectedStatusCode, string expectedDetail)
        {
            AssertObjectResult(result, expectedStatusCode, (p) =>
            {
                Assert.AreEqual(expectedDetail, p.Detail);
            });
        }

        public static void AssertObjectResult(object result, int expectedStatusCode, Action<ProblemDetails> extraAssert = null)
        {
            ObjectResult objectResult = result as ObjectResult;
            Assert.IsNotNull(objectResult);
            Assert.AreEqual(expectedStatusCode, objectResult.StatusCode);

            ProblemDetails problemDetails = objectResult.Value as ProblemDetails;
            Assert.IsNotNull(problemDetails);
            Assert.IsTrue(problemDetails.Status.HasValue);
            Assert.AreEqual(expectedStatusCode, problemDetails.Status.Value);
            if (extraAssert != null)
            {
                extraAssert(problemDetails);
            }
        }
    }
}
