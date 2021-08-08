using Kaiyuanshe.OpenHackathon.Server.Auth;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Models.Validations;
using Kaiyuanshe.OpenHackathon.Server.Swagger;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using System.ComponentModel.DataAnnotations;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Controllers
{
    public class RatingController : HackathonControllerBase
    {
        #region CreateRatingKind
        /// <summary>
        /// Create a new kind of rating.
        /// </summary>
        /// <param name="parameter"></param>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <returns>The rating kind</returns>
        /// <response code="200">Success. The response describes a rating kind.</response>
        [HttpPut]
        [ProducesResponseType(typeof(RatingKind), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 404)]
        [Route("hackathon/{hackathonName}/ratingKind")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.HackathonAdministrator)]
        public async Task<object> CreateRatingKind(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromBody] RatingKind parameter,
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

            // create rating kind
            parameter.hackathonName = hackathonName.ToLower();
            var ratingKindEntity = await RatingManagement.CreateRatingKindAsync(parameter, cancellationToken);
            return Ok(ResponseBuilder.BuildRatingKind(ratingKindEntity));
        }
        #endregion

        #region GetRatingKind
        /// <summary>
        /// Query a rating kind.
        /// </summary>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="kindId" example="d1e40c38-cc2a-445f-9eab-60c253256c57">Auto-generated Guid of a kind.</param>
        /// <returns>The rating kind</returns>
        /// <response code="200">Success. The response describes a rating kind.</response>
        [HttpGet]
        [ProducesResponseType(typeof(RatingKind), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 404)]
        [Route("hackathon/{hackathonName}/ratingKind/{kindId}")]
        public async Task<object> GetRatingKind(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required, Guid] string kindId,
            CancellationToken cancellationToken)
        {
            // validate hackathon
            var hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackathonName.ToLower(), cancellationToken);
            var options = new ValidateHackathonOptions
            {
                HackathonName = hackathonName,
                WritableRequired = false,
            };
            if (await ValidateHackathon(hackathon, options, cancellationToken) == false)
            {
                return options.ValidateResult;
            }

            // query rating kind
            var ratingKindEntity = await RatingManagement.GetRatingKindAsync(hackathonName.ToLower(), kindId, cancellationToken);
            if (ratingKindEntity == null)
            {
                return NotFound(Resources.Rating_KindNotFound);
            }
            return Ok(ResponseBuilder.BuildRatingKind(ratingKindEntity));
        }
        #endregion
    }
}
