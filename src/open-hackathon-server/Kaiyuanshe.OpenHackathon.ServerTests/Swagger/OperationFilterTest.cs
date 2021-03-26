using Kaiyuanshe.OpenHackathon.Server.Swagger;
using Microsoft.AspNetCore.Mvc.ApiExplorer;
using Microsoft.OpenApi.Models;
using NUnit.Framework;
using Swashbuckle.AspNetCore.SwaggerGen;
using System;
using System.Collections.Generic;
using System.Text;
using System.Linq;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Microsoft.AspNetCore.Mvc;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Swagger
{
    [TestFixture]
    public class OperationFilterTest : SwaggerTest
    {
        [Test]
        public void ErrorResonseOperationFilterTest()
        {
            var generator = Generate(
                   apiDescriptions: new[]
                   {
                       ApiDescriptionFactory.Create<FakeController>(
                        c => nameof(c.ActionWithNoParameters),
                        groupName: "v1",
                        httpMethod: "GET",
                        relativePath: "resource"),

                       ApiDescriptionFactory.Create<FakeController>(
                        c => nameof(c.ActionWithErrorResponseCodes),
                        groupName: "v1",
                        httpMethod: "POST",
                        relativePath: "resource"
                        ),
                   },
                   configure: (options) =>
                   {
                       options.OperationFilters.Add(new ErrorResponseOperationFilter());
                   }
            );

            var document = generator.GetSwagger("v1");

            var get = document.Paths["/resource"].Operations[OperationType.Get];
            Assert.AreEqual(1, get.Responses.Count); // Only the default 200 response
            Assert.IsTrue(get.Responses.ContainsKey("200"));

            var post = document.Paths["/resource"].Operations[OperationType.Post];
            Assert.AreEqual(7, post.Responses.Count); // default 200 + codes defined in attribute
            Assert.IsTrue(post.Responses.ContainsKey("200"));

            // 400
            Assert.IsTrue(post.Responses.ContainsKey("400"));
            Assert.AreEqual(1, post.Responses["400"].Content.Count);
            var schema = post.Responses["400"].Content.Values.Single().Schema;
            Assert.IsNotNull(schema.Reference);
            Assert.AreEqual(nameof(ValidationProblemDetails), schema.Reference.Id);
            Assert.IsNotNull(post.Responses["400"].Description);

            // other
            string[] codes = new string[] { "401", "403", "404", "412", "429" };
            foreach (var code in codes)
            {
                Assert.IsTrue(post.Responses.ContainsKey(code));
                Assert.AreEqual(1, post.Responses[code].Content.Count);
                schema = post.Responses[code].Content.Values.Single().Schema;
                Assert.IsNotNull(schema.Reference);
                Assert.AreEqual(nameof(ProblemDetails), schema.Reference.Id);
                Assert.IsNotNull(post.Responses[code].Description);
            }
        }

        [Test]
        public void UnauthorizedResponseOperationFilterTest()
        {
            var generator = Generate(
                   apiDescriptions: new[]
                   {
                       ApiDescriptionFactory.Create<FakeController>(
                        c => nameof(c.ActionWithTokenRequired),
                        groupName: "v1",
                        httpMethod: "GET",
                        relativePath: "resource"),
                   },
                   configure: (options) =>
                   {
                       options.OperationFilters.Add(new UnauthorizedResponseOperationFilter());
                   }
            );

            var document = generator.GetSwagger("v1");

            var get = document.Paths["/resource"].Operations[OperationType.Get];
            Assert.AreEqual(2, get.Responses.Count);
            Assert.IsTrue(get.Responses.ContainsKey("200"));
            Assert.IsTrue(get.Responses.ContainsKey("401"));
        }
    }
}
