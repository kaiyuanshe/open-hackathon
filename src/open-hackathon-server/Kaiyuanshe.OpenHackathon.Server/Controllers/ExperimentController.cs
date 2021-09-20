using Kaiyuanshe.OpenHackathon.Server.Auth;
using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Swagger;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using System.ComponentModel.DataAnnotations;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Controllers
{
    public class ExperimentController : HackathonControllerBase
    {
        public IExperimentManagement ExperimentManagement { get; set; }

        #region CreateTemplate
        /// <summary>
        /// Create a hackathon template for experiment. Currently only one template with name "default" is allowed.
        /// </summary>
        /// <param name="parameter"></param>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <returns>The award</returns>
        /// <response code="200">Success. The response describes a template.</response>
        [HttpPut]
        [ProducesResponseType(typeof(Template), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 404)]
        [Route("hackathon/{hackathonName}/template")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.HackathonAdministrator)]
        public async Task<object> CreateTemplate(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromBody] Template parameter,
            CancellationToken cancellationToken)
        {
            // validate hackathon
            var hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackathonName.ToLower(), cancellationToken);
            var options = new ValidateHackathonOptions
            {
                HackAdminRequird = true,
                HackathonName = hackathonName,
            };
            if (await ValidateHackathon(hackathon, options, cancellationToken) == false)
            {
                return options.ValidateResult;
            }

            // create template
            parameter.hackathonName = hackathonName.ToLower();
            parameter.name = "default";
            var context = await ExperimentManagement.CreateTemplateAsync(parameter, cancellationToken);
            return Ok(ResponseBuilder.BuildTemplate(context));
        }
        #endregion

        #region CreateExperiment
        /// <summary>
        /// Create a hackathon experiment. 
        /// Every enrolled user can create a predefined experiment for free.
        /// </summary>
        /// <param name="parameter"></param>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <returns>The award</returns>
        /// <response code="200">Success. The response describes a experiment.</response>
        [HttpPut]
        [ProducesResponseType(typeof(Experiment), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 404)]
        [Route("hackathon/{hackathonName}/experiment")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.LoginUser)]
        public async Task<object> CreateExperiment(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromBody] Experiment parameter,
            CancellationToken cancellationToken)
        {
            // validate hackathon
            var hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackathonName.ToLower(), cancellationToken);
            var options = new ValidateHackathonOptions
            {
                HackathonName = hackathonName,
            };
            if (await ValidateHackathon(hackathon, options, cancellationToken) == false)
            {
                return options.ValidateResult;
            }

            // validate enrollment
            var enrollment = await EnrollmentManagement.GetEnrollmentAsync(hackathonName.ToLower(), CurrentUserId, cancellationToken);
            var enrollmentOptions = new ValidateEnrollmentOptions
            {
                ApprovedRequired = true,
                HackathonName = hackathonName,
            };
            if (ValidateEnrollment(enrollment, enrollmentOptions) == false)
            {
                return enrollmentOptions.ValidateResult;
            }

            // TODO validate template. Template name is always `default` for now.

            // create experiment
            parameter.hackathonName = hackathonName.ToLower();
            parameter.templateName = "default";
            parameter.userId = CurrentUserId;
            var context = await ExperimentManagement.CreateExperimentAsync(parameter, cancellationToken);

            // build resp
            var userInfo = await GetCurrentUserInfo(cancellationToken);
            return Ok(ResponseBuilder.BuildExperiment(context, userInfo));
        }
        #endregion
    }
}
