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

namespace Kaiyuanshe.OpenHackathon.ServerTests.Swagger
{
    [TestFixture]
    public class OperationFilterTest : SwaggerTest
    {
        [Test]
        public void DefaultResonseOperationFilterTest()
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
                        c => nameof(c.ActionWithNoParameters),
                        groupName: "v1",
                        httpMethod: "POST",
                        relativePath: "resource",
                        supportedResponseTypes: new []
                        {
                            new ApiResponseType
                            {
                                ApiResponseFormats = new [] { new ApiResponseFormat { MediaType = "application/json" } },
                                StatusCode = 200,
                            },
                            new ApiResponseType
                            {
                                ApiResponseFormats = new [] { new ApiResponseFormat { MediaType = "application/json" } },
                                StatusCode = 400
                            }
                        }),
                   },
                   configure: (options) =>
                   {
                       options.OperationFilters.Add(new DefaultResponseOperationFilter());
                   }
            );

            var document = generator.GetSwagger("v1");

            var get = document.Paths["/resource"].Operations[OperationType.Get];
            Assert.AreEqual(1, get.Responses.Count); // Only the default 200 response
            Assert.IsTrue(get.Responses.ContainsKey("200"));

            var post = document.Paths["/resource"].Operations[OperationType.Post];
            Assert.AreEqual(2, post.Responses.Count);
            Assert.IsTrue(post.Responses.ContainsKey("400"));
            Assert.AreEqual(1, post.Responses["400"].Content.Count);
            var schema = post.Responses["400"].Content.Values.Single().Schema;
            Assert.IsNotNull(schema.Reference);
            Assert.AreEqual(nameof(ErrorResponse), schema.Reference.Id);
        }
    }
}
