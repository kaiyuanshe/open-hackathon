using Kaiyuanshe.OpenHackathon.Server.Auth;
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

            // check kind count
            bool canCreate = await RatingManagement.CanCreateRatingKindAsync(hackathonName.ToLower(), cancellationToken);
            if (!canCreate)
            {
                return PreconditionFailed(Resources.Rating_TooManyKinds);
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

            // valiate no ratings
            var ratingOptions = new RatingQueryOptions { RatingKindId = entity.Id };
            var hasRating = await RatingManagement.IsRatingCountGreaterThanZero(hackathonName.ToLower(), ratingOptions, cancellationToken);
            if (hasRating)
            {
                return PreconditionFailed(string.Format(Resources.Rating_HasRating, nameof(RatingKind)), kindId);
            }

            await RatingManagement.DeleteRatingKindAsync(hackathonName.ToLower(), kindId, cancellationToken);
            return NoContent();
        }
        #endregion

        private async Task<Rating> BuildRatingResp(RatingEntity ratingEntity,
            UserInfo judge = null,
            TeamEntity teamEntity = null,
            RatingKindEntity ratingKindEntity = null,
            CancellationToken cancellationToken = default)
        {
            if (judge == null)
            {
                judge = await UserManagement.GetUserByIdAsync(ratingEntity.JudgeId, cancellationToken);
            }

            if (teamEntity == null)
            {
                teamEntity = await TeamManagement.GetTeamByIdAsync(ratingEntity.HackathonName, ratingEntity.TeamId, cancellationToken);
            }
            var teamCreator = await UserManagement.GetUserByIdAsync(teamEntity.CreatorId, cancellationToken);
            var team = ResponseBuilder.BuildTeam(teamEntity, teamCreator);

            if (ratingKindEntity == null)
            {
                ratingKindEntity = await RatingManagement.GetCachedRatingKindAsync(ratingEntity.HackathonName, ratingEntity.RatingKindId, cancellationToken);
            }
            var kind = ResponseBuilder.BuildRatingKind(ratingKindEntity);

            var rating = ResponseBuilder.BuildRating(ratingEntity, judge, team, kind);
            return rating;
        }

        #region CreateRating
        /// <summary>
        /// Create a new rating.
        /// </summary>
        /// <param name="parameter"></param>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <returns>The rating</returns>
        /// <response code="200">Success. The response describes a rating.</response>
        [HttpPut]
        [ProducesResponseType(typeof(Rating), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 403, 404)]
        [Route("hackathon/{hackathonName}/rating")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.HackathonJudge)]
        public async Task<object> CreateRating(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromBody, HttpPutPolicy] Rating parameter,
            CancellationToken cancellationToken)
        {
            // validate hackathon
            var hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackathonName.ToLower(), cancellationToken);
            var options = new ValidateHackathonOptions
            {
                HackJudgeRequird = true,
                OnlineRequired = true,
                HackathonName = hackathonName,
            };
            if (await ValidateHackathon(hackathon, options, cancellationToken) == false)
            {
                return options.ValidateResult;
            }

            // validate team
            var team = await TeamManagement.GetTeamByIdAsync(hackathonName.ToLower(), parameter.teamId, cancellationToken);
            var validateTeamOptions = new ValidateTeamOptions
            {
                HackathonName = hackathonName,
            };
            if (await ValidateTeam(team, validateTeamOptions, cancellationToken) == false)
            {
                return validateTeamOptions.ValidateResult;
            }

            // validate kind
            var kind = await RatingManagement.GetRatingKindAsync(hackathonName.ToLower(), parameter.ratingKindId, cancellationToken);
            var validateKindOptions = new ValidateRatingKindOptions
            {
                ScoreInRangeRequired = true,
                ScoreInRequest = parameter.score.GetValueOrDefault(0)
            };
            if (ValidateRatingKind(kind, validateKindOptions) == false)
            {
                return validateKindOptions.ValidateResult;
            }

            // create
            parameter.hackathonName = hackathonName.ToLower();
            parameter.judgeId = CurrentUserId;
            var ratingEntity = await RatingManagement.CreateRatingAsync(parameter, cancellationToken);
            var ratingResponse = await BuildRatingResp(ratingEntity, null, team, kind, cancellationToken);
            return Ok(ratingResponse);
        }
        #endregion

        #region UpdateRating
        /// <summary>
        /// Update a rating. Only score and description are allowed to edit. Other properties in request body are ignored if present.
        /// </summary>
        /// <param name="parameter"></param>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="ratingId" example="dd09af6d-75f6-463c-8e5d-786818e409db">Auto-generated Guid of a rating.</param>
        /// <returns>The rating</returns>
        /// <response code="200">Success. The response describes a rating.</response>
        [HttpPatch]
        [ProducesResponseType(typeof(Rating), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 403, 404)]
        [Route("hackathon/{hackathonName}/rating/{ratingId}")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.HackathonJudge)]
        public async Task<object> UpdateRating(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required, Guid] string ratingId,
            [FromBody] Rating parameter,
            CancellationToken cancellationToken)
        {
            // validate hackathon
            var hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackathonName.ToLower(), cancellationToken);
            var options = new ValidateHackathonOptions
            {
                HackJudgeRequird = true,
                OnlineRequired = true,
                HackathonName = hackathonName,
            };
            if (await ValidateHackathon(hackathon, options, cancellationToken) == false)
            {
                return options.ValidateResult;
            }

            // Get Rating
            var ratingEntity = await RatingManagement.GetRatingAsync(hackathonName.ToLower(), ratingId, cancellationToken);
            if (ratingEntity == null)
            {
                return NotFound(Resources.Rating_NotFound);
            }
            if (ratingEntity.JudgeId != CurrentUserId)
            {
                bool isAdmin = await HackathonAdminManagement.IsHackathonAdmin(hackathonName.ToLower(), User, cancellationToken);
                if (!isAdmin)
                {
                    return Forbidden(Resources.Rating_OnlyCreator);
                }
            }

            // validate kind
            var kind = await RatingManagement.GetRatingKindAsync(hackathonName.ToLower(), ratingEntity.RatingKindId, cancellationToken);
            var validateKindOptions = new ValidateRatingKindOptions
            {
                ScoreInRangeRequired = true,
                ScoreInRequest = parameter.score.GetValueOrDefault(ratingEntity.Score)
            };
            if (ValidateRatingKind(kind, validateKindOptions) == false)
            {
                return validateKindOptions.ValidateResult;
            }

            // update
            ratingEntity = await RatingManagement.UpdateRatingAsync(ratingEntity, parameter, cancellationToken);
            var ratingResponse = await BuildRatingResp(ratingEntity, null, null, kind, cancellationToken);
            return Ok(ratingResponse);
        }
        #endregion

        #region ListPaginatedRatings
        /// <summary>
        /// List paginated ratings, per service paging.
        /// </summary>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="ratingKindId" example="e4576366-fa87-451d-8e4d-ef6d1b6cee05">optional id of a rating kind. if present, only ratings of this kind is returned.</param>
        /// <param name="teamId" example="d1e40c38-cc2a-445f-9eab-60c253256c57">optional id of a team. if present, only ratings of the team returned.</param>
        /// <param name="judgeId" example="1">optional userId of a judge. If present, only ratings provided by the judge returned.</param>
        /// <returns>a list of ratings</returns>
        /// <response code="200">Success. The response describes a list of ratings and a nullable link to query more results.</response>
        [HttpGet]
        [ProducesResponseType(typeof(RatingList), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 404)]
        [Route("hackathon/{hackathonName}/ratings")]
        public async Task<object> ListPaginatedRatings(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromQuery, Guid] string ratingKindId,
            [FromQuery, Guid] string teamId,
            [FromQuery] string judgeId,
            [FromQuery] Pagination pagination,
            CancellationToken cancellationToken)
        {
            // validate hackathon
            var hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackathonName.ToLower(), cancellationToken);
            var options = new ValidateHackathonOptions
            {
                WritableRequired = false,
                HackathonName = hackathonName,
            };
            if (await ValidateHackathon(hackathon, options, cancellationToken) == false)
            {
                return options.ValidateResult;
            }

            // list
            var ratingQueryOptions = new RatingQueryOptions
            {
                RatingKindId = ratingKindId,
                JudgeId = judgeId,
                TeamId = teamId,
                TableContinuationToken = pagination.ToContinuationToken(),
                Top = pagination.top,
            };
            var ratings = await RatingManagement.ListPaginatedRatingsAsync(hackathonName.ToLower(), ratingQueryOptions, cancellationToken);

            // resp
            var routeValues = new RouteValueDictionary();
            if (pagination.top.HasValue)
            {
                routeValues.Add(nameof(pagination.top), pagination.top.Value);
            }
            if (!string.IsNullOrWhiteSpace(ratingKindId))
            {
                routeValues.Add(nameof(ratingKindId), ratingKindId);
            }
            if (!string.IsNullOrWhiteSpace(teamId))
            {
                routeValues.Add(nameof(teamId), teamId);
            }
            if (!string.IsNullOrWhiteSpace(judgeId))
            {
                routeValues.Add(nameof(judgeId), judgeId);
            }
            var nextLink = BuildNextLinkUrl(routeValues, ratings.ContinuationToken);

            var list = await ResponseBuilder.BuildResourceListAsync<RatingEntity, Rating, RatingList>(
                ratings,
                (ratingEntity, ct) => BuildRatingResp(ratingEntity, cancellationToken: ct),
                nextLink,
                cancellationToken);
            return Ok(list);
        }
        #endregion

        #region GetRating
        /// <summary>
        /// Get a rating. 
        /// </summary>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="ratingId" example="dd09af6d-75f6-463c-8e5d-786818e409db">Auto-generated Guid of a rating.</param>
        /// <returns>The rating</returns>
        /// <response code="200">Success. The response describes a rating.</response>
        [HttpGet]
        [ProducesResponseType(typeof(Rating), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 404)]
        [Route("hackathon/{hackathonName}/rating/{ratingId}")]
        public async Task<object> GetRating(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required, Guid] string ratingId,
            CancellationToken cancellationToken)
        {
            // validate hackathon
            var hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackathonName.ToLower(), cancellationToken);
            var options = new ValidateHackathonOptions
            {
                WritableRequired = false,
                HackathonName = hackathonName,
            };
            if (await ValidateHackathon(hackathon, options, cancellationToken) == false)
            {
                return options.ValidateResult;
            }

            // Get Rating
            var ratingEntity = await RatingManagement.GetRatingAsync(hackathonName.ToLower(), ratingId, cancellationToken);
            if (ratingEntity == null)
            {
                return NotFound(Resources.Rating_NotFound);
            }

            // get
            var ratingResponse = await BuildRatingResp(ratingEntity, null, null, null, cancellationToken);
            return Ok(ratingResponse);
        }
        #endregion

        #region DeleteRating
        /// <summary>
        /// Delete a rating. Only hackathon adminstrator or the submitter can delete it.
        /// </summary>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="ratingId" example="dd09af6d-75f6-463c-8e5d-786818e409db">Auto-generated Guid of a rating.</param>
        /// <response code="204">Success. The response indicates the rating is deleted.</response>
        [HttpDelete]
        [SwaggerErrorResponse(400, 403, 404)]
        [Route("hackathon/{hackathonName}/rating/{ratingId}")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.HackathonJudge)]
        public async Task<object> DeleteRating(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required, Guid] string ratingId,
            CancellationToken cancellationToken)
        {
            // validate hackathon
            var hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackathonName.ToLower(), cancellationToken);
            var options = new ValidateHackathonOptions
            {
                HackJudgeRequird = true,
                HackathonName = hackathonName,
            };
            if (await ValidateHackathon(hackathon, options, cancellationToken) == false)
            {
                return options.ValidateResult;
            }

            // Get Rating
            var ratingEntity = await RatingManagement.GetRatingAsync(hackathonName.ToLower(), ratingId, cancellationToken);
            if (ratingEntity == null)
            {
                return NoContent();
            }

            // delete
            if (ratingEntity.JudgeId != CurrentUserId)
            {
                bool isAdmin = await HackathonAdminManagement.IsHackathonAdmin(hackathonName.ToLower(), User, cancellationToken);
                if (!isAdmin)
                {
                    return Forbidden(Resources.Rating_OnlyCreator);
                }
            }
            await RatingManagement.DeleteRatingAsync(hackathonName.ToLower(), ratingId, cancellationToken);
            return NoContent();
        }
        #endregion
    }
}
