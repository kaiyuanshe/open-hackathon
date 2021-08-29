using Kaiyuanshe.OpenHackathon.Server.Auth;
using Kaiyuanshe.OpenHackathon.Server.Biz;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.ResponseBuilder;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Routing;
using Microsoft.WindowsAzure.Storage.Table;
using System;
using System.Linq;
using System.Net.Mime;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Controllers
{
    [ApiController]
    [Consumes(MediaTypeNames.Application.Json)]
    [Produces(MediaTypeNames.Application.Json)]
    [Route("v2")]
    public abstract class HackathonControllerBase : ControllerBase
    {
        public IAuthorizationService AuthorizationService { get; set; }

        public IResponseBuilder ResponseBuilder { get; set; }

        public IHackathonManagement HackathonManagement { get; set; }
        public IHackathonAdminManagement HackathonAdminManagement { get; set; }

        public IUserManagement UserManagement { get; set; }

        public IEnrollmentManagement EnrollmentManagement { get; set; }

        public IAwardManagement AwardManagement { get; set; }

        public ITeamManagement TeamManagement { get; set; }

        public IFileManagement FileManagement { get; set; }

        public IWorkManagement WorkManagement { get; set; }

        public IJudgeManagement JudgeManagement { get; set; }

        public IRatingManagement RatingManagement { get; set; }

        /// <summary>
        /// Id of current User. Return string.Empty if token is not required or invalid.
        /// </summary>
        protected string CurrentUserId
        {
            get
            {
                return ClaimsHelper.GetUserId(User);
            }
        }

        protected async Task<UserInfo> GetCurrentUserInfo(CancellationToken cancellationToken = default)
        {
            if (string.IsNullOrWhiteSpace(CurrentUserId))
                return null;

            return await UserManagement.GetUserByIdAsync(CurrentUserId, cancellationToken);
        }

        /// <summary>
        /// Get nextLink url for paginated results
        /// </summary>
        /// <param name="routeValues">values to generate url. Values of current url are implicitly used. 
        /// Add extra key/value pairs or modifications to routeValues. Values not used in route will be appended as QueryString.</param>
        /// <returns></returns>
        protected string BuildNextLinkUrl(RouteValueDictionary routeValues, TableContinuationToken continuationToken)
        {
            if (continuationToken == null)
                return null;

            if (routeValues == null)
            {
                routeValues = new RouteValueDictionary();
            }
            routeValues.Add(nameof(Pagination.np), continuationToken.NextPartitionKey);
            routeValues.Add(nameof(Pagination.nr), continuationToken.NextRowKey);

            if (EnvHelper.IsRunningInTests())
            {
                // Unit Test
                StringBuilder stringBuilder = new StringBuilder();
                foreach (var key in routeValues.Keys)
                {
                    stringBuilder.Append($"&{key}={routeValues[key]}");
                }
                return stringBuilder.ToString();
            }

            return Url.Action(
               ControllerContext.ActionDescriptor.ActionName,
               ControllerContext.ActionDescriptor.ControllerName,
               routeValues,
               "https", // Request.Scheme doesn't work well on App Service containers. TLS terminates on front end, the traffic to containers are always http.
               Request.Host.Value);
        }

        #region ObjectResult with ProblemDetails
        protected ObjectResult BadRequest(string detail, string instance = null)
        {
            return Problem(
                statusCode: 400,
                detail: detail,
                instance: instance);
        }

        protected ObjectResult Unauthorized(string detail, string instance = null)
        {
            return Problem(
                statusCode: 401,
                detail: detail,
                instance: instance);
        }

        protected ObjectResult Forbidden(string detail, string instance = null)
        {
            return Problem(
                statusCode: 403,
                detail: detail,
                instance: instance);
        }

        protected ObjectResult NotFound(string detail, string instance = null)
        {
            return Problem(
                statusCode: 404,
                detail: detail,
                instance: instance);
        }

        protected ObjectResult Conflict(string detail, string instance = null)
        {
            return Problem(
                statusCode: 409,
                detail: detail,
                instance: instance);
        }

        protected ObjectResult PreconditionFailed(string detail, string instance = null)
        {
            return Problem(
                statusCode: 412,
                detail: detail,
                instance: instance
            );
        }
        #endregion

        #region Frequently used validations

        public class ControllerValiationOptions
        {
            /// <summary>
            /// null if validate successfully. Otherwise a response which desribes the failure
            /// and can be returned to client.
            /// </summary>
            public object ValidateResult { get; set; }

            /// <summary>
            /// optional hackathon name for error message 
            /// </summary>
            public string HackathonName { get; set; } = string.Empty;

            /// <summary>
            /// optional Team Id for error message 
            /// </summary>
            public string TeamId { get; set; } = string.Empty;

            /// <summary>
            /// optional {userId} in Route for error message
            /// </summary>
            public string UserId { get; set; } = string.Empty;

        }

        public class ValidateHackathonOptions : ControllerValiationOptions
        {
            /// <summary>
            /// default to 'true'
            /// </summary>
            public bool WritableRequired { get; set; } = true;
            public bool EnrollmentOpenRequired { get; set; }
            public bool EnrollmentNotFullRequired { get; set; }
            public bool HackathonOpenRequired { get; set; }
            public bool HackAdminRequird { get; set; }
            public bool HackJudgeRequird { get; set; }
            public bool OnlineRequired { get; set; }
            public bool NotDeletedRequired { get; set; }
        }

        public class ValidateEnrollmentOptions : ControllerValiationOptions
        {
            public bool ApprovedRequired { get; set; }
        }

        public class ValidateTeamOptions : ControllerValiationOptions
        {
            public bool TeamAdminRequired { get; set; }
            public bool NoAwardAssignmentRequired { get; set; }
            public bool NoRatingRequired { get; set; }
        }

        public class ValidateTeamMemberOptions : ControllerValiationOptions
        {
            public bool ApprovedMemberRequired { get; set; }
        }

        public class ValidateAwardOptions : ControllerValiationOptions
        {
            public AwardTarget NewTarget { get; set; }
            /// <summary>
            /// Validate where award.target is allowed to change to NewTarget
            /// </summary>
            public bool TargetChangableRequired { get; set; }

            public bool QuantityCheckRequired { get; set; }

            public string AssigneeId { get; set; }
            public bool AssigneeExistRequired { get; set; }
        }

        public class ValidateRatingKindOptions : ControllerValiationOptions
        {
            public int ScoreInRequest { get; set; }
            public bool ScoreInRangeRequired { get; set; }
        }

        #region ValidateHackathon
        protected async Task<bool> ValidateHackathon(HackathonEntity hackathon,
            ValidateHackathonOptions options,
            CancellationToken cancellationToken = default)
        {
            options.ValidateResult = null; // make sure it's not set by caller

            if (hackathon == null)
            {
                options.ValidateResult = NotFound(string.Format(Resources.Hackathon_NotFound, options.HackathonName));
                return false;
            }

            if (options.WritableRequired && hackathon.ReadOnly)
            {
                options.ValidateResult = Forbidden(Resources.Hackathon_ReadOnly);
                return false;
            }

            if (options.OnlineRequired && hackathon.Status != HackathonStatus.online)
            {
                options.ValidateResult = NotFound(string.Format(Resources.Hackathon_NotFound, options.HackathonName));
                return false;
            }

            if (options.NotDeletedRequired && hackathon.Status == HackathonStatus.offline)
            {
                options.ValidateResult = PreconditionFailed(string.Format(Resources.Hackathon_Deleted, options.HackathonName));
                return false;
            }

            if (options.HackathonOpenRequired)
            {
                if (hackathon.EventStartedAt.HasValue && DateTime.UtcNow < hackathon.EventStartedAt.Value)
                {
                    // event not started
                    options.ValidateResult = PreconditionFailed(Resources.Hackathon_NotStarted);
                    return false;
                }

                if (hackathon.EventEndedAt.HasValue && DateTime.UtcNow > hackathon.EventEndedAt.Value)
                {
                    // event ended
                    options.ValidateResult = PreconditionFailed(string.Format(Resources.Hackathon_Ended, hackathon.EventEndedAt.Value));
                    return false;
                }
            }

            if (options.EnrollmentOpenRequired)
            {
                if (hackathon.EnrollmentStartedAt.HasValue && DateTime.UtcNow < hackathon.EnrollmentStartedAt.Value)
                {
                    // enrollment not started
                    options.ValidateResult = PreconditionFailed(string.Format(Resources.Enrollment_NotStarted, hackathon.EnrollmentStartedAt.Value));
                    return false;
                }

                if (hackathon.EnrollmentEndedAt.HasValue && DateTime.UtcNow > hackathon.EnrollmentEndedAt.Value)
                {
                    // enrollment ended
                    options.ValidateResult = PreconditionFailed(string.Format(Resources.Enrollment_Ended, hackathon.EnrollmentEndedAt.Value));
                    return false;
                }
            }

            if (options.EnrollmentNotFullRequired)
            {
                if (hackathon.MaxEnrollment > 0 && hackathon.Enrollment >= hackathon.MaxEnrollment)
                {
                    // too many enrollments
                    options.ValidateResult = PreconditionFailed(Resources.Enrollment_Full);
                    return false;
                }
            }

            if (options.HackAdminRequird)
            {
                var authorizationResult = await AuthorizationService.AuthorizeAsync(User, hackathon, AuthConstant.Policy.HackathonAdministrator);
                if (!authorizationResult.Succeeded)
                {
                    options.ValidateResult = Forbidden(Resources.Hackathon_NotAdmin);
                    return false;
                }
            }

            if (options.HackJudgeRequird)
            {
                var authorizationResult = await AuthorizationService.AuthorizeAsync(User, hackathon, AuthConstant.Policy.HackathonJudge);
                if (!authorizationResult.Succeeded)
                {
                    options.ValidateResult = Forbidden(Resources.Hackathon_NotJudge);
                    return false;
                }
            }

            return true;
        }
        #endregion

        #region ValidateEnrollment
        protected bool ValidateEnrollment(EnrollmentEntity enrollment, ValidateEnrollmentOptions options)
        {
            if (enrollment == null)
            {
                options.ValidateResult = NotFound(string.Format(Resources.Enrollment_NotFound, options.UserId ?? CurrentUserId, options.HackathonName));
                return false;
            }

            if (options.ApprovedRequired && enrollment.Status != EnrollmentStatus.approved)
            {
                options.ValidateResult = PreconditionFailed(Resources.Enrollment_NotApproved);
                return false;
            }

            return true;
        }
        #endregion

        #region ValidateTeam
        protected async Task<bool> ValidateTeam(TeamEntity team,
            ValidateTeamOptions options,
            CancellationToken cancellationToken = default)
        {
            if (team == null)
            {
                options.ValidateResult = NotFound(Resources.Team_NotFound);
                return false;
            }

            if (options.TeamAdminRequired)
            {
                var authorizationResult = await AuthorizationService.AuthorizeAsync(User, team, AuthConstant.Policy.TeamAdministrator);
                if (!authorizationResult.Succeeded)
                {
                    options.ValidateResult = Forbidden(Resources.Team_NotAdmin);
                    return false;
                }
            }

            if (options.NoAwardAssignmentRequired)
            {
                var assignments = await AwardManagement.ListAssignmentsByTeamAsync(team.HackathonName, team.Id, cancellationToken);
                if (assignments.Count() > 0)
                {
                    options.ValidateResult = PreconditionFailed(Resources.Team_HasAward);
                    return false;
                }
            }

            if (options.NoRatingRequired)
            {
                // valiate no ratings
                var ratingOptions = new RatingQueryOptions { TeamId = team.Id };
                var hasRating = await RatingManagement.IsRatingCountGreaterThanZero(team.HackathonName, ratingOptions, cancellationToken);
                if (hasRating)
                {
                    options.ValidateResult = PreconditionFailed(string.Format(Resources.Rating_HasRating, nameof(Team)), team.Id);
                    return false;
                }
            }

            return true;
        }
        #endregion

        #region ValidateTeamMember
        protected async Task<bool> ValidateTeamMember(TeamEntity team, TeamMemberEntity teamMember,
            ValidateTeamMemberOptions options,
            CancellationToken cancellationToken)
        {
            if (team == null)
            {
                options.ValidateResult = NotFound(Resources.Team_NotFound);
                return false;
            }

            if (teamMember == null || teamMember.TeamId != team.Id)
            {
                options.ValidateResult = NotFound(string.Format(Resources.TeamMember_NotFound, options.UserId ?? CurrentUserId, options.TeamId));
                return false;
            }

            if (options.ApprovedMemberRequired)
            {
                var authorizationResult = await AuthorizationService.AuthorizeAsync(User, team, AuthConstant.Policy.TeamMember);
                if (!authorizationResult.Succeeded)
                {
                    options.ValidateResult = Forbidden(string.Format(Resources.TeamMember_AccessDenied, CurrentUserId));
                    return false;
                }
            }

            return true;
        }
        #endregion

        #region ValidateAward
        protected async Task<bool> ValidateAward(AwardEntity award, ValidateAwardOptions options, CancellationToken cancellationToken = default)
        {
            if (award == null)
            {
                options.ValidateResult = NotFound(Resources.Award_NotFound);
                return false;
            }

            if (options.TargetChangableRequired && award.Target != options.NewTarget)
            {
                var assignmentCount = await AwardManagement.GetAssignmentCountAsync(award.HackathonName, award.Id, cancellationToken);
                if (assignmentCount > 0)
                {
                    options.ValidateResult = PreconditionFailed(Resources.Award_CannotUpdateTarget);
                    return false;
                }
            }

            if (options.QuantityCheckRequired)
            {
                var assignmentCount = await AwardManagement.GetAssignmentCountAsync(award.HackathonName, award.Id, cancellationToken);
                if (assignmentCount >= award.Quantity)
                {
                    options.ValidateResult = PreconditionFailed(string.Format(Resources.Award_TooManyAssignments, award.Quantity));
                    return false;
                }
            }

            if (options.AssigneeExistRequired)
            {
                switch (award.Target)
                {
                    case AwardTarget.team:
                        var team = await TeamManagement.GetTeamByIdAsync(award.HackathonName, options.AssigneeId, cancellationToken);
                        if (team == null)
                        {
                            options.ValidateResult = NotFound(Resources.Team_NotFound);
                            return false;
                        }
                        break;
                    case AwardTarget.individual:
                        var enrollment = await EnrollmentManagement.GetEnrollmentAsync(award.HackathonName, options.AssigneeId, cancellationToken);
                        if (enrollment == null || enrollment.Status != EnrollmentStatus.approved)
                        {
                            options.ValidateResult = NotFound(string.Format(Resources.Enrollment_NotFound, options.AssigneeId, award.HackathonName));
                            return false;
                        }
                        break;
                    default:
                        break;
                }
            }

            return true;
        }
        #endregion

        #region ValidateRatingKind
        protected bool ValidateRatingKind(RatingKindEntity ratingKindEntity, ValidateRatingKindOptions options)
        {
            if (ratingKindEntity == null)
            {
                options.ValidateResult = NotFound(Resources.Rating_KindNotFound);
                return false;
            }

            if (options.ScoreInRangeRequired)
            {
                if (options.ScoreInRequest > ratingKindEntity.MaximumScore)
                {
                    options.ValidateResult = BadRequest(string.Format(Resources.Rating_ScoreNotInRange, ratingKindEntity.MaximumScore));
                    return false;
                }
            }

            return true;
        }
        #endregion

        #endregion
    }
}
