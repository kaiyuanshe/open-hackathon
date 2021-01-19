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

namespace Kaiyuanshe.OpenHackathon.Server.Swagger
{
    /// <summary>
    /// Add <seealso cref="ErrorResponse"/> to Http responses whose statusCode is >=400.
    /// </summary>
    public class DefaultResponseOperationFilter : IOperationFilter
    {
        public static readonly string DefaultCode = "default";

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
}
