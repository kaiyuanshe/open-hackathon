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
        internal static Dictionary<int, string> statusCodeDescriptions = new Dictionary<int, string>
        {
            { 400, "Bad Reqeuest. The server cannot or will not process the request due to something that is perceived to be a client error. e.g., malformed request syntax"},
            { 401, "Unauthorized. The client doesn't have valid authentication credentials."},
            { 403, "Forbidden. Access to the requested resource is forbidden. The server understood the request but refuse to fulfill it."},
            { 404, "Not Found. The server cannot find the requested resource."},
            { 409, "Conflict. The request could not be processed because of conflict in the current state of the resource, such as an edit conflict between multiple simultaneous updates."},
            { 412, "Precondition Failed. The server does not meet one of the preconditions that the requester put on the request header fields."},
            { 413, "Payload Too Large. The request is larger than the server is willing or able to process."},
            { 429, "Too Many Requests. The client has sent too many requests in a given amount of time."},
        };

        public void Apply(OpenApiOperation operation, OperationFilterContext context)
        {
            var problemDetailsSchema = context.SchemaGenerator.GenerateSchema(typeof(ProblemDetails), context.SchemaRepository);
            var validationProblemDetailsSchema = context.SchemaGenerator.GenerateSchema(typeof(ValidationProblemDetails), context.SchemaRepository);

            var swaggerErrorRespAttrs = context.MethodInfo.GetCustomAttributes<SwaggerErrorResponseAttribute>();
            var statusCodes = swaggerErrorRespAttrs.SelectMany(e => e.StatusCodes).ToHashSet();
            foreach (var statusCode in statusCodes)
            {
                var errorRespSchema = statusCode == 400 ? validationProblemDetailsSchema : problemDetailsSchema;
                if (operation.Responses.ContainsKey(statusCode.ToString()))
                {
                    operation.Responses[statusCode.ToString()].Content = new Dictionary<string, OpenApiMediaType>
                    {
                        ["application/json"] = new OpenApiMediaType
                        {
                            Schema = errorRespSchema
                        }
                    };
                }
                else
                {
                    operation.Responses.Add(statusCode.ToString(), new OpenApiResponse
                    {
                        Content = new Dictionary<string, OpenApiMediaType>
                        {
                            ["application/json"] = new OpenApiMediaType
                            {
                                Schema = errorRespSchema
                            }
                        },
                    });
                }

                if (statusCodeDescriptions.ContainsKey(statusCode))
                {
                    operation.Responses[statusCode.ToString()].Description = statusCodeDescriptions[statusCode];
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
                    Description = ErrorResponseOperationFilter.statusCodeDescriptions[401],
                });

                // Add Required header
                if (operation.Parameters == null)
                {
                    operation.Parameters = new List<OpenApiParameter>();
                }
            }
        }
    }
}
