using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.OpenApi.Models;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using System.IO;
using System.Reflection;
using Swashbuckle.AspNetCore.SwaggerGen;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Filters;

namespace Kaiyuanshe.OpenHackathon.Server.Swagger
{
    /// <summary>
    /// Add <seealso cref="ErrorResponse"/> to Http responses whose statusCode is >=400. 
    /// The statusCode must be explicitly added to the method like: &lt;response code="400"&gt;Bad Request&lt;/response&gt;. 
    /// </summary>
    public class ErrorResponseOperationFilter : IOperationFilter
    {
        public void Apply(OpenApiOperation operation, OperationFilterContext context)
        {
            var errorRespSchema = context.SchemaGenerator.GenerateSchema(typeof(ErrorResponse), context.SchemaRepository);
            foreach (var resp in operation.Responses)
            {
                if (int.TryParse(resp.Key, out int httpStatusCode) && httpStatusCode >= 400)
                {
                    resp.Value.Content = new Dictionary<string, OpenApiMediaType>
                    {
                        ["application/json"] = new OpenApiMediaType
                        {
                            Schema = errorRespSchema
                        }
                    };
                }
            }
        }
    }

    /// <summary>
    /// Add 401 response to schema for all methods annotated with <seealso cref="TokenRequiredAttribute"/>
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

            var errorRespSchema = context.SchemaGenerator.GenerateSchema(typeof(ErrorResponse), context.SchemaRepository);
            var tokenRequiredAttrs = context.MethodInfo.GetCustomAttributes<TokenRequiredAttribute>();
            if (tokenRequiredAttrs.SingleOrDefault() != null)
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
                });

                // Add Required header
                if (operation.Parameters == null)
                    operation.Parameters = new List<OpenApiParameter>();

               
            }
        }
    }
}
