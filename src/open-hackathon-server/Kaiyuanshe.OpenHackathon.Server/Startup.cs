using Autofac;
using Autofac.Extensions.DependencyInjection;
using Kaiyuanshe.OpenHackathon.Server.Auth;
using Kaiyuanshe.OpenHackathon.Server.Controllers;
using Kaiyuanshe.OpenHackathon.Server.CronJobs;
using Kaiyuanshe.OpenHackathon.Server.DependencyInjection;
using Kaiyuanshe.OpenHackathon.Server.Middlewares;
using Kaiyuanshe.OpenHackathon.Server.ResponseBuilder;
using Kaiyuanshe.OpenHackathon.Server.Swagger;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Infrastructure;
using Microsoft.AspNetCore.Server.Kestrel.Core;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using System;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace Kaiyuanshe.OpenHackathon.Server
{
    public class Startup
    {
        public Startup(IConfiguration configuration)
        {
            Configuration = configuration;
        }

        public IConfiguration Configuration { get; }

        public ILifetimeScope AutofacContainer { get; private set; }

        // ConfigureServices is where you register dependencies. This gets
        // called by the runtime before the ConfigureContainer method, below.
        public void ConfigureServices(IServiceCollection services)
        {
            // Add services to the collection. Don't build or return
            // any IServiceProvider or the ConfigureContainer method
            // won't get called. Don't create a ContainerBuilder
            // for Autofac here, and don't call builder.Populate() - that
            // happens in the AutofacServiceProviderFactory for you.
            services
                .AddMvc(mvcOptions =>
                {
                    mvcOptions.EnableEndpointRouting = false;
                })
                .AddControllersAsServices()
                .AddJsonOptions(options =>
                {
                    options.JsonSerializerOptions.Converters.Add(new JsonStringEnumConverter(JsonNamingPolicy.CamelCase));
                });
            services.AddTransient<ProblemDetailsFactory, CustomProblemDetailsFactory>();
            services.Configure<KestrelServerOptions>(options =>
            {
                options.AllowSynchronousIO = true;
            });

            // Razor pages
            services.AddRazorPages(options =>
            {
                options.Conventions.AllowAnonymousToPage("/Index");
                options.Conventions.AllowAnonymousToFolder("/Authing");
            });

            // AuthN & AuthZ
            RegisterAuthorizeHandlers(services);

            // Cron Jobs
            services.AddHostedService<CronJobHostedService>();

            // Register the Swagger generator, defining 1 or more Swagger documents
            SwaggerStartup.ConfigureService(services);

        }

        // ConfigureContainer is where you can register things directly
        // with Autofac. This runs after ConfigureServices so the things
        // here will override registrations made in ConfigureServices.
        // Don't build the container; that gets done for you by the factory.
        public void ConfigureContainer(ContainerBuilder builder)
        {
            // Register your own things directly with Autofac here. Don't
            // call builder.Populate(), that happens in AutofacServiceProviderFactory
            // for you.
            builder.RegisterModule(new HackathonDefaultModule());
            RegisterControllers(builder);
        }

        // Configure is where you add middleware. This is called after
        // ConfigureContainer. You can use IApplicationBuilder.ApplicationServices
        // here if you need to resolve things from the container.
        public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
        {
            // If, for some reason, you need a reference to the built container, you
            // can use the convenience extension method GetAutofacRoot.
            AutofacContainer = app.ApplicationServices.GetAutofacRoot();

            if (env.IsDevelopment())
            {
                app.UseDeveloperExceptionPage();
            }
            else
            {
                app.UseExceptionHandler("/error");
            }

            // app.UseHttpsRedirection();
            app.UseRouting();
            app.UseAuthentication();
            app.UseAuthorization();

            // middleware
            // In asp.net core 3.0, middlewares must be registered before MapControllers
            RegisterMiddlewares(app);

            app.UseEndpoints(endpoints =>
            {
                endpoints.MapControllers();
                endpoints.MapRazorPages();
            });

            // Configure Swagger
            SwaggerStartup.Configure(app, env);
        }

        private void RegisterMiddlewares(IApplicationBuilder app)
        {
            app.UseMiddleware<HttpHeadersMiddleware>();
            app.UseMiddleware<LoggingMiddleware>();
            app.UseMvc();
        }

        private void RegisterControllers(ContainerBuilder builder)
        {
            var controllers = typeof(HackathonControllerBase).SubTypes();
            builder.RegisterTypes(controllers).PropertiesAutowired();
        }

        private void RegisterAuthorizeHandlers(IServiceCollection services)
        {
            services.AddSingleton<IAuthorizationHandler, PlatformAdministratorHandler>();
            services.AddSingleton<IAuthorizationHandler, HackathonAdministratorHandler>();
            services.AddSingleton<IAuthorizationHandler, HackathonJudgeHandler>();
            services.AddSingleton<IAuthorizationHandler, TeamAdministratorHandler>();
            services.AddSingleton<IAuthorizationHandler, TeamMemberHandler>();
            services.AddSingleton<IAuthorizationHandler, NoRequirementHandler>();

            services.AddAuthentication(options =>
            {
                options.AddScheme<DefaultAuthHandler>(AuthConstant.AuthType.Token, AuthConstant.AuthType.Token);
                options.DefaultScheme = AuthConstant.AuthType.Token;
            });

            Action<AuthorizationPolicyBuilder> noRequirementPolicy = policy =>
            {
                policy.Requirements.Add(new NoRequirement());
            };

            services.AddAuthorization(options =>
            {
                // real policies
                options.AddPolicy(AuthConstant.Policy.PlatformAdministrator, policy =>
                {
                    policy.Requirements.Add(new PlatformAdministratorRequirement());
                });
                options.AddPolicy(AuthConstant.Policy.HackathonAdministrator, policy =>
                {
                    policy.Requirements.Add(new HackathonAdministratorRequirement());
                });
                options.AddPolicy(AuthConstant.Policy.HackathonJudge, policy =>
                {
                    policy.Requirements.Add(new HackathonJudgeRequirement());
                });
                options.AddPolicy(AuthConstant.Policy.TeamAdministrator, policy =>
                {
                    policy.Requirements.Add(new TeamAdministratorRequirement());
                });
                options.AddPolicy(AuthConstant.Policy.TeamMember, policy =>
                {
                    policy.Requirements.Add(new TeamMemberRequirement());
                });

                // empty policies to make swagger UI happy
                options.AddPolicy(AuthConstant.PolicyForSwagger.HackathonAdministrator, noRequirementPolicy);
                options.AddPolicy(AuthConstant.PolicyForSwagger.HackathonJudge, noRequirementPolicy);
                options.AddPolicy(AuthConstant.PolicyForSwagger.TeamAdministrator, noRequirementPolicy);
                options.AddPolicy(AuthConstant.PolicyForSwagger.TeamMember, noRequirementPolicy);
                options.AddPolicy(AuthConstant.PolicyForSwagger.LoginUser, noRequirementPolicy);
            });
        }
    }
}
