using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.OpenApi.Models;
using Swashbuckle.AspNetCore.SwaggerGen;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;

namespace Kaiyuanshe.OpenHackathon.Server.Swagger
{
    /// <summary>
    /// Add <seealso cref="ProblemDetails"/> to Http responses whose statusCode is >=400. 
    /// The statusCode must be explicitly added to the method like: &lt;response code="400"&gt;Bad Request&lt;/response&gt;. 
    /// </summary>
    public class ErrorResponseOperationFilter : IOperationFilter
    {
        public void Apply(OpenApiOperation operation, OperationFilterContext context)
        {
            var problemDetailsSchema = context.SchemaGenerator.GenerateSchema(typeof(ProblemDetails), context.SchemaRepository);
            var validationProblemDetailsSchema = context.SchemaGenerator.GenerateSchema(typeof(ValidationProblemDetails), context.SchemaRepository);
            foreach (var resp in operation.Responses)
            {
                if (int.TryParse(resp.Key, out int httpStatusCode) && httpStatusCode >= 400)
                {
                    var schema = httpStatusCode == 400 ? validationProblemDetailsSchema : problemDetailsSchema;
                    resp.Value.Content = new Dictionary<string, OpenApiMediaType>
                    {
                        ["application/json"] = new OpenApiMediaType
                        {
                            Schema = schema
                        }
                    };
                }
            }
        }
    }

    /// <summary>
    /// Add 401 response to schema for all methods annotated with <seealso cref="AuthorizeAttribute"/>
    /// </summary>
    public class UnauthorizedResponseOperationFilter : IOperationFilter
    {
        public void Apply(OpenApiOperation operation, OperationFilterContext context)
        {
            if (operation.Responses.ContainsKey("401"))
            {
                // in case 401 is explicitly added
                return;
            }

            var errorRespSchema = context.SchemaGenerator.GenerateSchema(typeof(ProblemDetails), context.SchemaRepository);
            var authorizeAttrs = context.MethodInfo.GetCustomAttributes<AuthorizeAttribute>();
            if (authorizeAttrs.SingleOrDefault() != null)
            {
                // Add 401 response to Swagger
                operation.Responses.Add("401", new OpenApiResponse
                {
                    Content = new Dictionary<string, OpenApiMediaType>
                    {
                        ["application/json"] = new OpenApiMediaType
                        {
                            Schema = errorRespSchema
                        }
                    },
                    Description = "Unauthorized. Token missing or invalid.",
                });

                // Add Required header
                if (operation.Parameters == null)
                    operation.Parameters = new List<OpenApiParameter>();


            }
        }
    }
}
