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

namespace Kaiyuanshe.OpenHackathon.Server.Swagger
{
    public class SwaggerStartup
    {
        private static readonly string ApiVersion = "v2.0";
        private static readonly string ApiSpecTitle = "Open Hackathon API Specification 2.0";

        public static void ConfigureService(IServiceCollection services)
        {
            services.AddSwaggerGen((options) =>
            {
                // metadata
                options.SwaggerDoc("v2.0", new OpenApiInfo
                {
                    Contact = new OpenApiContact
                    {
                        Email = "infra@kaiyuanshe.org",
                        Name = "开源社",
                        Url = new Uri("https://kaiyuanshe.cn/")
                    },
                    Description = ApiSpecTitle,
                    License = new OpenApiLicense
                    {
                        Name = "MIT License",
                        Url = new Uri("https://github.com/kaiyuanshe/open-hackathon/blob/master/LICENSE.md")
                    },
                    Title = ApiSpecTitle,
                    Version = ApiVersion,
                });

                // tags
                options.TagActionsBy(api => new List<string> { "OpenHackathon" });

                // Set the comments path for the Swagger JSON and UI.
                var xmlFile = $"{Assembly.GetExecutingAssembly().GetName().Name}.xml";
                var xmlPath = Path.Combine(AppContext.BaseDirectory, xmlFile);
                options.IncludeXmlComments(xmlPath);

                // Operation Filters
                options.OperationFilter<DefaultResponseOperationFilter>();
            });
        }

        public static void Configure(IApplicationBuilder app, IWebHostEnvironment env)
        {
            // Enable middleware to serve generated Swagger as a JSON endpoint.
            app.UseSwagger((options) =>
            {
                options.PreSerializeFilters.Add((doc, req) =>
                {
                });
            });

            // Enable middleware to serve swagger-ui (HTML, JS, CSS, etc.),
            // specifying the Swagger JSON endpoint.
            app.UseSwaggerUI(c =>
            {
                c.SwaggerEndpoint("/swagger/v2.0/swagger.json", ApiSpecTitle);
            });

            app.UseRouting();
            app.UseEndpoints(endpoints =>
            {
                endpoints.MapControllers();
            });
        }
    }
}
