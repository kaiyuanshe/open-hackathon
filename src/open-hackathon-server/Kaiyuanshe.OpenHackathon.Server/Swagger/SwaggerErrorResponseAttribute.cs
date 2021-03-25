using System;

namespace Kaiyuanshe.OpenHackathon.Server.Swagger
{
    [AttributeUsage(AttributeTargets.Method, Inherited = false, AllowMultiple = true)]
    public sealed class SwaggerErrorResponseAttribute : Attribute
    {
        public int[] StatusCodes { get; }

        // This is a positional argument
        public SwaggerErrorResponseAttribute(params int[] statusCodes)
        {
            StatusCodes = statusCodes;
        }
    }
}