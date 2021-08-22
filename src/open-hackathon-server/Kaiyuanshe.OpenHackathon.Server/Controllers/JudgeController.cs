using Kaiyuanshe.OpenHackathon.Server.Auth;
using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Models;
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
    public class JudgeController : HackathonControllerBase
    {
        #region CreateJudge
        /// <summary>
        /// Add a new judge
        /// </summary>
        /// <param name="parameter"></param>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="userId" example="1">Id of user</param>
        /// <returns>The judge</returns>
        /// <response code="200">Success. The response describes a judge.</response>
        [HttpPut]
        [ProducesResponseType(typeof(Judge), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 404, 412)]
        [Route("hackathon/{hackathonName}/judge/{userId}")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.HackathonAdministrator)]
        public async Task<object> CreateJudge(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required] string userId,
            [FromBody] Judge parameter,
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

            // validate user
            var user = await UserManagement.GetUserByIdAsync(userId, cancellationToken);
            if (user == null)
            {
                return NotFound(Resources.User_NotFound);
            }

            // check judge count
            bool canCreate = await JudgeManagement.CanCreateJudgeAsync(hackathonName.ToLower(), cancellationToken);
            if (!canCreate)
            {
                return PreconditionFailed(Resources.Judge_TooMany);
            }

            // create judge
            parameter.hackathonName = hackathonName.ToLower();
            parameter.userId = userId;
            var entity = await JudgeManagement.CreateJudgeAsync(parameter, cancellationToken);
            return Ok(ResponseBuilder.BuildJudge(entity, user));
        }
        #endregion

        #region UpdateJudge
        /// <summary>
        /// Update a judge
        /// </summary>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="userId" example="1">Id of user</param>
        /// <response code="200">Success. The response describes a judge.</response>
        [HttpPatch]
        [ProducesResponseType(typeof(Judge), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 404)]
        [Route("hackathon/{hackathonName}/judge/{userId}")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.HackathonAdministrator)]
        public async Task<object> UpdateJudge(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required] string userId,
            [FromBody] Judge parameter,
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

            // validate user
            var user = await UserManagement.GetUserByIdAsync(userId, cancellationToken);
            if (user == null)
            {
                return NotFound(Resources.User_NotFound);
            }

            // query and update judge
            var entity = await JudgeManagement.GetJudgeAsync(hackathonName.ToLower(), userId, cancellationToken);
            if (entity == null)
            {
                return NotFound(Resources.Judge_NotFound);
            }
            entity = await JudgeManagement.UpdateJudgeAsync(entity, parameter, cancellationToken);
            return Ok(ResponseBuilder.BuildJudge(entity, user));
        }
        #endregion

        #region GetJudge
        /// <summary>
        /// Query a judge
        /// </summary>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="userId" example="1">Id of user</param>
        /// <returns>The judge</returns>
        /// <response code="200">Success. The response describes a judge.</response>
        [HttpGet]
        [ProducesResponseType(typeof(Judge), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 404)]
        [Route("hackathon/{hackathonName}/judge/{userId}")]
        public async Task<object> GetJudge(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required] string userId,
            CancellationToken cancellationToken)
        {
            // validate hackathon
            var hackathon = await HackathonManagement.GetHackathonEntityByNameAsync(hackathonName.ToLower(), cancellationToken);
            var options = new ValidateHackathonOptions
            {
                OnlineRequired = true,
                WritableRequired = false,
                HackathonName = hackathonName
            };
            if (await ValidateHackathon(hackathon, options, cancellationToken) == false)
            {
                return options.ValidateResult;
            }

            // validate user
            var user = await UserManagement.GetUserByIdAsync(userId, cancellationToken);
            if (user == null)
            {
                return NotFound(Resources.User_NotFound);
            }

            // create judge
            var entity = await JudgeManagement.GetJudgeAsync(hackathonName.ToLower(), userId, cancellationToken);
            if (entity == null)
            {
                return NotFound(Resources.Judge_NotFound);
            }
            return Ok(ResponseBuilder.BuildJudge(entity, user));
        }
        #endregion

        #region ListJudgesByHackathon
        /// <summary>
        /// List paginated judges of a hackathon.
        /// </summary>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <returns>the response contains a list of judges and a nextLink if there are more results.</returns>
        /// <response code="200">Success. The response describes a list of judge and a nullable link to query more results.</response>
        [HttpGet]
        [ProducesResponseType(typeof(JudgeList), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 404)]
        [Route("hackathon/{hackathonName}/judges")]
        public async Task<object> ListJudgesByHackathon(
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
            var judgeQueryOptions = new JudgeQueryOptions
            {
                TableContinuationToken = pagination.ToContinuationToken(),
                Top = pagination.top,
            };
            var judges = await JudgeManagement.ListPaginatedJudgesAsync(hackathonName.ToLower(), judgeQueryOptions, cancellationToken);
            var routeValues = new RouteValueDictionary();
            if (pagination.top.HasValue)
            {
                routeValues.Add(nameof(pagination.top), pagination.top.Value);
            }
            var nextLink = BuildNextLinkUrl(routeValues, judgeQueryOptions.Next);

            // build resp
            var resp = await ResponseBuilder.BuildResourceListAsync<JudgeEntity, Judge, JudgeList>(
                judges,
                async (judge, ct) =>
                {
                    var userInfo = await UserManagement.GetUserByIdAsync(judge.UserId, ct);
                    return ResponseBuilder.BuildJudge(judge, userInfo);
                },
                nextLink);

            return Ok(resp);
        }
        #endregion

        #region DeleteJudge
        /// <summary>
        /// Delete a judge. Please make sure all related ratings are already deleted.
        /// </summary>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="userId" example="1">Id of user</param>
        /// <response code="204">Deleted</response>
        [HttpDelete]
        [SwaggerErrorResponse(400, 404, 412)]
        [Route("hackathon/{hackathonName}/judge/{userId}")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.HackathonAdministrator)]
        public async Task<object> DeleteJudge(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required] string userId,
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

            // validate user
            var user = await UserManagement.GetUserByIdAsync(userId, cancellationToken);
            if (user == null)
            {
                return NotFound(Resources.User_NotFound);
            }

            // query and delete judge
            var entity = await JudgeManagement.GetJudgeAsync(hackathonName.ToLower(), userId, cancellationToken);
            if (entity == null)
            {
                return NoContent();
            }

            // valiate no ratings
            var ratingOptions = new RatingQueryOptions { JudgeId = userId };
            var hasRating = await RatingManagement.IsRatingCountGreaterThanZero(hackathonName.ToLower(), ratingOptions, cancellationToken);
            if (hasRating)
            {
                return PreconditionFailed(string.Format(Resources.Rating_HasRating, nameof(Judge)), userId);
            }
            await JudgeManagement.DeleteJudgeAsync(hackathonName.ToLower(), userId, cancellationToken);
            return NoContent();
        }
        #endregion
    }
}
