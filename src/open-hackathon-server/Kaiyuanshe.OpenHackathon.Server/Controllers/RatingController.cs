﻿using Kaiyuanshe.OpenHackathon.Server.Auth;
using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Models.Validations;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Kaiyuanshe.OpenHackathon.Server.Swagger;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Routing;
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
        [SwaggerErrorResponse(400, 404, 412)]
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

        #region UpdateRatingKind
        /// <summary>
        /// Update a kind of rating.
        /// </summary>
        /// <param name="parameter"></param>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="kindId" example="e4576366-fa87-451d-8e4d-ef6d1b6cee05">Auto-generated Guid of a kind.</param>
        /// <returns>The rating kind</returns>
        /// <response code="200">Success. The response describes a rating kind.</response>
        [HttpPatch]
        [ProducesResponseType(typeof(RatingKind), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 404, 412)]
        [Route("hackathon/{hackathonName}/ratingKind/{kindId}")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.HackathonAdministrator)]
        public async Task<object> UpdateRatingKind(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required, Guid] string kindId,
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

            // Query Rating Kind
            var ratingKindEntity = await RatingManagement.GetRatingKindAsync(hackathonName.ToLower(), kindId, cancellationToken);
            if (ratingKindEntity == null)
            {
                return NotFound(Resources.Rating_KindNotFound);
            }

            // Update rating kind
            ratingKindEntity = await RatingManagement.UpdateRatingKindAsync(ratingKindEntity, parameter, cancellationToken);
            return Ok(ResponseBuilder.BuildRatingKind(ratingKindEntity));
        }
        #endregion

        #region GetRatingKind
        /// <summary>
        /// Query a rating kind.
        /// </summary>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="kindId" example="e4576366-fa87-451d-8e4d-ef6d1b6cee05">Auto-generated Guid of a kind.</param>
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

        #region ListRatingKinds
        /// <summary>
        /// List paginated rating kinds of a hackathon.
        /// </summary>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <returns>the response contains a list of ratingKinds and a nextLink if there are more results.</returns>
        /// <response code="200">Success.</response>
        [HttpGet]
        [ProducesResponseType(typeof(RatingKindList), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 404)]
        [Route("hackathon/{hackathonName}/ratingKinds")]
        public async Task<object> ListRatingKinds(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromQuery] Pagination pagination,
            CancellationToken cancellationToken)
        {
            // validate hackathon
            var hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackathonName.ToLower());
            var options = new ValidateHackathonOptions
            {
                HackathonName = hackathonName,
                WritableRequired = false,
            };
            if (await ValidateHackathon(hackathon, options) == false)
            {
                return options.ValidateResult;
            }

            // query
            var ratingKindQueryOptions = new RatingKindQueryOptions
            {
                TableContinuationToken = pagination.ToContinuationToken(),
                Top = pagination.top
            };

            var ratingKinds = await RatingManagement.ListPaginatedRatingKindsAsync(hackathonName.ToLower(), ratingKindQueryOptions, cancellationToken);
            var routeValues = new RouteValueDictionary();
            if (pagination.top.HasValue)
            {
                routeValues.Add(nameof(pagination.top), pagination.top.Value);
            }
            var nextLink = BuildNextLinkUrl(routeValues, ratingKindQueryOptions.Next);
            return Ok(ResponseBuilder.BuildResourceList<RatingKindEntity, RatingKind, RatingKindList>(
                    ratingKinds,
                    ResponseBuilder.BuildRatingKind,
                    nextLink));
        }
        #endregion

        #region DeleteRatingKind
        /// <summary>
        /// Delete a rating kind. Please make sure all related ratings are already deleted.
        /// </summary>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="kindId" example="e4576366-fa87-451d-8e4d-ef6d1b6cee05">Auto-generated Guid of a kind.</param>
        /// <response code="204">Deleted</response>
        [HttpDelete]
        [SwaggerErrorResponse(400, 404, 412)]
        [Route("hackathon/{hackathonName}/ratingKind/{kindId}")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.HackathonAdministrator)]
        public async Task<object> DeleteRatingKind(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required, Guid] string kindId,
            CancellationToken cancellationToken)
        {
            // validate hackathon
            var hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackathonName.ToLower(), cancellationToken);
            var options = new ValidateHackathonOptions
            {
                HackAdminRequird = true,
                HackathonName = hackathonName
            };
            if (await ValidateHackathon(hackathon, options, cancellationToken) == false)
            {
                return options.ValidateResult;
            }

            // query and delete judge
            var entity = await RatingManagement.GetRatingKindAsync(hackathonName.ToLower(), kindId, cancellationToken);
            if (entity == null)
            {
                return NoContent();
            }
            await RatingManagement.DeleteRatingKindAsync(hackathonName.ToLower(), kindId, cancellationToken);
            return NoContent();
        }
        #endregion

    }
}