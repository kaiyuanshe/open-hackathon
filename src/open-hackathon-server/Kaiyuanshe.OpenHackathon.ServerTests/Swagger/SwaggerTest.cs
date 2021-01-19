using Microsoft.AspNetCore.Mvc.ApiExplorer;
using Microsoft.OpenApi.Models;
using Swashbuckle.AspNetCore.SwaggerGen;
using System;
using System.Collections.Generic;
using System.Text;
using System.Text.Json;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Swagger
{
    public class SwaggerTest
    {
        public SwaggerGenerator Generate(IEnumerable<ApiDescription> apiDescriptions, Action<SwaggerGeneratorOptions> configure = null)
        {
            var options = DefaultOptions;
            configure?.Invoke(options);
            return new SwaggerGenerator(
                options,
                new FakeApiDescriptionGroupCollectionProvider(apiDescriptions),
                new SchemaGenerator(new SchemaGeneratorOptions(), new JsonSerializerDataContractResolver(new JsonSerializerOptions()))
            );
        }

        private static readonly SwaggerGeneratorOptions DefaultOptions = new SwaggerGeneratorOptions
        {
            SwaggerDocs = new Dictionary<string, OpenApiInfo>
            {
                ["v1"] = new OpenApiInfo { Version = "V1", Title = "Test API" },
            },
            DocumentFilters = new List<IDocumentFilter>(),
            OperationFilters = new List<IOperationFilter>(),
        };
    }
}
