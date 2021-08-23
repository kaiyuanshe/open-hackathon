using Kaiyuanshe.OpenHackathon.Server.Auth;
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
    public class AdminController : HackathonControllerBase
    {
        #region CreateAdmin
        /// <summary>
        /// Add an user as hackathon admin.
        /// </summary>
        /// <param name="hackathonName" example="foo">Name of hackathon. Case-insensitive.
        /// Must contain only letters and/or numbers, length between 1 and 100</param>
        /// <param name="userId" example="1">Id of user</param>
        /// <returns>The admin</returns>
        /// <response code="200">Success. The response describes an admin.</response>
        [HttpPut]
        [ProducesResponseType(typeof(HackathonAdmin), StatusCodes.Status200OK)]
        [SwaggerErrorResponse(400, 404, 412)]
        [Route("hackathon/{hackathonName}/admin/{userId}")]
        [Authorize(Policy = AuthConstant.PolicyForSwagger.HackathonAdministrator)]
        public async Task<object> CreateAdmin(
            [FromRoute, Required, RegularExpression(ModelConstants.HackathonNamePattern)] string hackathonName,
            [FromRoute, Required] string userId,
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

            // create admin
            var admin = new HackathonAdmin
            {
                hackathonName = hackathonName.ToLower(),
                userId = userId,
            };
            var adminEntity = await HackathonAdminManagement.CreateAdminAsync(admin, cancellationToken);
            var resp = ResponseBuilder.BuildHackathonAdmin(adminEntity, user);
            return Ok(resp);
        }
        #endregion
    }
}
