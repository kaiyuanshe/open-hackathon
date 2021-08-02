﻿using Kaiyuanshe.OpenHackathon.Server.Auth;
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

            // create judge
            parameter.hackathonName = hackathonName.ToLower();
            parameter.userId = userId;
            var entity = await JudgeManagement.CreateJudgeAsync(parameter, cancellationToken);
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
    }
}
