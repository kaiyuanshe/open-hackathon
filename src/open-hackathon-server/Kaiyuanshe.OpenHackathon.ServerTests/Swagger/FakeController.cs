using Kaiyuanshe.OpenHackathon.Server.Swagger;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System;
using System.ComponentModel.DataAnnotations;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Swagger
{
    public class FakeController
    {
        public void ActionWithNoParameters()
        { }

        public void ActionWithParameter(string param)
        { }

        public void ActionWithMultipleParameters(string param1, int param2)
        { }

        [HttpGet(Name = "SomeRouteName")]
        public void ActionWithRouteNameMetadata()
        { }

        [Obsolete]
        public void ActionWithObsoleteAttribute()
        { }

        [Authorize]
        public void ActionWithTokenRequired()
        { }

        [SwaggerErrorResponse(400, 401)]
        [SwaggerErrorResponse(400, 403, 412)]
        [SwaggerErrorResponse(403, 404, 429)]
        public void ActionWithErrorResponseCodes()
        { }

        public void ActionWithParameterWithRequiredAttribute([Required] string param)
        { }

        public void ActionWithIntParameter(int param)
        { }

        public void ActionWithIntParameterWithRangeAttribute([Range(1, 12)] int param)
        { }

        public void ActionWithIntParameterWithDefaultValue(int param = 1)
        { }

        public void ActionWithIntParameterWithRequiredAttribute([Required] int param)
        { }

        [Consumes("application/someMediaType")]
        public void ActionWithConsumesAttribute(string param)
        { }

        public int ActionWithReturnValue()
        {
            throw new NotImplementedException();
        }

        [Produces("application/someMediaType")]
        public int ActionWithProducesAttribute()
        {
            throw new NotImplementedException();
        }
    }
}
