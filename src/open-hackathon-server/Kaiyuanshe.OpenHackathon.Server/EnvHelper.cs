using System;
using System.Linq;

namespace Kaiyuanshe.OpenHackathon.Server
{
    public static class EnvHelper
    {
        public static bool IsDevelopment()
        {
            // https://docs.microsoft.com/en-us/aspnet/core/fundamentals/environments?view=aspnetcore-5.0#environments
            var envName = "ASPNETCORE_ENVIRONMENT";
            if (Environment.GetEnvironmentVariable(envName, EnvironmentVariableTarget.Process) == "Development"
                || Environment.GetEnvironmentVariable(envName, EnvironmentVariableTarget.User) == "Development"
                || Environment.GetEnvironmentVariable(envName, EnvironmentVariableTarget.Machine) == "Development")
            {
                return true;
            }

            return false;
        }

        public static bool IsRunningInTests()
        {
            var assemblies = AppDomain.CurrentDomain.GetAssemblies();
            return assemblies.Any(a => a.FullName.ToLower().StartsWith("nunit.framework"));
        }
    }
}
