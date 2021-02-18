using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System.Collections.Generic;
using System.Net.Mime;

namespace Kaiyuanshe.OpenHackathon.Server.Controllers
{
    [ApiController]
    [Consumes(MediaTypeNames.Application.Json)]
    [Produces(MediaTypeNames.Application.Json)]
    [Route("v2")]
    public abstract class HackathonControllerBase : ControllerBase
    {
        public IAuthorizationService AuthorizationService { get; set; }

        protected IList<string> GetErrors()
        {
            var modelErrors = new List<string>();
            foreach (var modelState in ModelState.Values)
            {
                foreach (var modelError in modelState.Errors)
                {
                    modelErrors.Add(modelError.ErrorMessage);
                }
            }

            return modelErrors;
        }
    }
}
