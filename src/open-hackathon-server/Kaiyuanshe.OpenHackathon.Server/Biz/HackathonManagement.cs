using Kaiyuanshe.OpenHackathon.Server.Auth;
using Kaiyuanshe.OpenHackathon.Server.Cache;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.Extensions.Logging;
using Microsoft.WindowsAzure.Storage.Table;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Claims;
using System.Threading;
using System.Threading.Tasks;


namespace Kaiyuanshe.OpenHackathon.Server.Biz
{
    public interface IHackathonManagement
    {
        /// <summary>
        /// Is user eligible to create new hackathon. Might be throttled. 
        /// </summary>
        Task<bool> CanCreateHackathonAsync(ClaimsPrincipal user, CancellationToken cancellationToken);

        /// <summary>
        /// Create a new hackathon
        /// </summary>
        Task<HackathonEntity> CreateHackathonAsync(Hackathon request, CancellationToken cancellationToken = default);

        /// <summary>
        /// Update hackathon from request.
        /// </summary>
        Task<HackathonEntity> UpdateHackathonAsync(Hackathon request, CancellationToken cancellationToken = default);

        /// <summary>
        /// Change the status of a hackathon.
        /// </summary>
        Task<HackathonEntity> UpdateHackathonStatusAsync(HackathonEntity hackathonEntity, HackathonStatus status, CancellationToken cancellationToken = default);

        Task<HackathonEntity> UpdateHackathonReadOnlyAsync(HackathonEntity hackathon, bool readOnly, CancellationToken cancellation);

        /// <summary>
        /// Get Hackathon By name. Return null if not found.
        /// </summary>
        Task<HackathonEntity> GetHackathonEntityByNameAsync(string name, CancellationToken cancellationToken = default);

        /// <summary>
        /// Search paginated hackathon
        /// </summary>
        Task<IEnumerable<HackathonEntity>> ListPaginatedHackathonsAsync(ClaimsPrincipal user, HackathonQueryOptions options, CancellationToken cancellationToken = default);

        /// <summary>
        /// List all hackathons
        /// </summary>
        Task<Dictionary<string, HackathonEntity>> ListAllHackathonsAsync(CancellationToken cancellationToken = default);

        /// <summary>
        /// Get roles of a user on a specified hackathon
        /// </summary>
        Task<HackathonRoles> GetHackathonRolesAsync(HackathonEntity hackathon, ClaimsPrincipal user, CancellationToken cancellationToken = default);

        /// <summary>
        /// Get roles of a user on a list of hackathon
        /// </summary>
        Task<IEnumerable<Tuple<HackathonEntity, HackathonRoles>>> ListHackathonRolesAsync(IEnumerable<HackathonEntity> hackathons, ClaimsPrincipal user, CancellationToken cancellationToken = default);
    }

    /// <inheritdoc cref="IHackathonManagement"/>
    public class HackathonManagement : ManagementClientBase, IHackathonManagement
    {
        static readonly int MaxHackathonsEachDay = 3;
        static readonly int MaxHackathonsEachMonth = 10;

        private readonly ILogger logger;
        internal static string cacheKeyForAllHackathon = CacheKeys.GetCacheKey(CacheEntryType.Hackathon, "all");

        public IHackathonAdminManagement HackathonAdminManagement { get; set; }

        public IEnrollmentManagement EnrollmentManagement { get; set; }

        public IJudgeManagement JudgeManagement { get; set; }

        public HackathonManagement(ILogger<HackathonManagement> logger)
        {
            this.logger = logger;
        }

        #region Hackathon Cache
        private void InvalidateCacheAllHackathon()
        {
            // TODO need better cache strategy to:
            //  1. Partially update cache;
            //  2. cache required data only like those for filter/ordering
            Cache.Remove(cacheKeyForAllHackathon);
        }
        #endregion

        #region Task<bool> CanCreateHackathonAsync(ClaimsPrincipal user, CancellationToken cancellationToken)
        public async Task<bool> CanCreateHackathonAsync(ClaimsPrincipal user, CancellationToken cancellationToken)
        {
            var userId = ClaimsHelper.GetUserId(user);
            if (string.IsNullOrWhiteSpace(userId))
                return false;

            // cannot create >3 in each day or >10 in each month
            var allHackathons = await ListAllHackathonsAsync(cancellationToken);
            var myCreated = allHackathons.Values.Where(h => h.CreatorId == userId);

            var thisDay = myCreated.Count(h => h.CreatedAt > DateTime.UtcNow.AddDays(-1));
            if (thisDay >= MaxHackathonsEachDay)
            {
                logger.LogInformation($"{userId} created {thisDay} hackathons in the past 24 hours, cannot create more.");
                return false;
            }

            var thisMonth = myCreated.Count(h => h.CreatedAt > DateTime.UtcNow.AddMonths(-1));
            if (thisMonth >= MaxHackathonsEachMonth)
            {
                logger.LogInformation($"{userId} created {thisMonth} hackathons in the past month, cannot create more.");
                return false;
            }

            return true;
        }
        #endregion

        #region CreateHackathonAsync
        public async Task<HackathonEntity> CreateHackathonAsync(Hackathon request, CancellationToken cancellationToken = default)
        {
            #region Insert HackathonEntity
            var entity = new HackathonEntity
            {
                PartitionKey = request.name,
                RowKey = string.Empty,
                AutoApprove = request.autoApprove.HasValue ? request.autoApprove.Value : false,
                Ribbon = request.ribbon,
                Status = HackathonStatus.planning,
                Summary = request.summary,
                Tags = request.tags,
                MaxEnrollment = request.maxEnrollment.HasValue ? request.maxEnrollment.Value : 0,
                Banners = request.banners,
                CreatedAt = DateTime.UtcNow,
                CreatorId = request.creatorId,
                Detail = request.detail,
                DisplayName = request.displayName,
                EventStartedAt = request.eventStartedAt,
                EventEndedAt = request.eventEndedAt,
                EnrollmentStartedAt = request.enrollmentStartedAt,
                EnrollmentEndedAt = request.enrollmentEndedAt,
                JudgeStartedAt = request.judgeStartedAt,
                JudgeEndedAt = request.judgeEndedAt,
                Location = request.location,
                ReadOnly = false,
            };
            await StorageContext.HackathonTable.InsertAsync(entity, cancellationToken);
            InvalidateCacheAllHackathon();
            #endregion

            #region Add creator as Admin
            await HackathonAdminManagement.CreateAdminAsync(new HackathonAdmin
            {
                hackathonName = request.name,
                userId = request.creatorId,
            }, cancellationToken);
            #endregion

            return entity;
        }
        #endregion CreateHackathonAsync

        #region UpdateHackathonStatusAsync
        public async Task<HackathonEntity> UpdateHackathonStatusAsync(HackathonEntity hackathonEntity, HackathonStatus status, CancellationToken cancellationToken = default)
        {
            if (hackathonEntity == null || hackathonEntity.Status == status)
                return hackathonEntity;

            hackathonEntity.Status = status;
            await StorageContext.HackathonTable.MergeAsync(hackathonEntity, cancellationToken);

            InvalidateCacheAllHackathon();
            return hackathonEntity;
        }
        #endregion

        #region Task<HackathonEntity> UpdateHackathonReadOnlyAsync(HackathonEntity hackathon, bool readOnly, CancellationToken cancellation)
        public async Task<HackathonEntity> UpdateHackathonReadOnlyAsync(HackathonEntity hackathon, bool readOnly, CancellationToken cancellation)
        {
            if (hackathon == null)
                return hackathon;

            hackathon.ReadOnly = readOnly;
            await StorageContext.HackathonTable.MergeAsync(hackathon, cancellation);
            return hackathon;
        }
        #endregion

        #region GetHackathonEntityByNameAsync
        public async Task<HackathonEntity> GetHackathonEntityByNameAsync(string name, CancellationToken cancellationToken = default)
        {
            var entity = await StorageContext.HackathonTable.RetrieveAsync(name, string.Empty, cancellationToken);
            return entity;
        }
        #endregion

        #region UpdateHackathonAsync
        public async Task<HackathonEntity> UpdateHackathonAsync(Hackathon request, CancellationToken cancellationToken = default)
        {
            await StorageContext.HackathonTable.RetrieveAndMergeAsync(request.name, string.Empty, (entity) =>
            {
                entity.Ribbon = request.ribbon ?? entity.Ribbon;
                entity.Summary = request.summary ?? entity.Summary;
                entity.Detail = request.detail ?? entity.Detail;
                entity.Location = request.location ?? entity.Location;
                entity.Banners = request.banners ?? entity.Banners;
                entity.DisplayName = request.displayName ?? entity.DisplayName;
                if (request.maxEnrollment.HasValue)
                    entity.MaxEnrollment = request.maxEnrollment.Value;
                if (request.autoApprove.HasValue)
                    entity.AutoApprove = request.autoApprove.Value;
                entity.Tags = request.tags ?? entity.Tags;
                if (request.eventStartedAt.HasValue)
                    entity.EventStartedAt = request.eventStartedAt.Value;
                if (request.eventEndedAt.HasValue)
                    entity.EventEndedAt = request.eventEndedAt.Value;
                if (request.enrollmentStartedAt.HasValue)
                    entity.EnrollmentStartedAt = request.enrollmentStartedAt.Value;
                if (request.enrollmentEndedAt.HasValue)
                    entity.EnrollmentEndedAt = request.enrollmentEndedAt.Value;
                if (request.judgeStartedAt.HasValue)
                    entity.JudgeStartedAt = request.judgeStartedAt.Value;
                if (request.judgeEndedAt.HasValue)
                    entity.JudgeEndedAt = request.judgeEndedAt.Value;
            }, cancellationToken);
            var updated = await StorageContext.HackathonTable.RetrieveAsync(request.name, string.Empty, cancellationToken);
            InvalidateCacheAllHackathon();
            return updated;
        }
        #endregion

        #region List Paginated Hackathons
        private IEnumerable<HackathonEntity> OrderAndPaging(HackathonQueryOptions options, IEnumerable<HackathonEntity> candidtes)
        {
            // ordering
            IEnumerable<HackathonEntity> hackathons = candidtes;
            var orderBy = options?.OrderBy.GetValueOrDefault(HackathonOrderBy.createdAt);
            switch (orderBy)
            {
                case HackathonOrderBy.updatedAt:
                    hackathons = hackathons.OrderByDescending(h => h.Timestamp);
                    break;
                case HackathonOrderBy.hot:
                    hackathons = hackathons.OrderByDescending(h => h.Enrollment);
                    break;
                default:
                    hackathons = hackathons.OrderByDescending(h => h.CreatedAt);
                    break;
            }

            // paging
            int np = 0;
            int.TryParse(options.TableContinuationToken?.NextPartitionKey, out np);
            int top = options.Top.GetValueOrDefault(100);
            hackathons = hackathons.Skip(np).Take(top);

            // next paging
            options.Next = null;
            if (np + top < candidtes.Count())
            {
                options.Next = new TableContinuationToken
                {
                    NextPartitionKey = (np + top).ToString(),
                    NextRowKey = (np + top).ToString(),
                };
            }

            return hackathons;
        }

        private async Task<IEnumerable<HackathonEntity>> ListOnlineHackathons(HackathonQueryOptions options, CancellationToken cancellationToken)
        {
            IEnumerable<HackathonEntity> hackathons = (await ListAllHackathonsAsync(cancellationToken)).Values;

            hackathons = hackathons.Where(h => h.Status == HackathonStatus.online);
            return hackathons;
        }

        private async Task<IEnumerable<HackathonEntity>> ListAdminHackathons(ClaimsPrincipal user, HackathonQueryOptions options, CancellationToken cancellationToken)
        {
            if (user == null)
            {
                return new List<HackathonEntity>();
            }
            string userId = ClaimsHelper.GetUserId(user);
            if (string.IsNullOrWhiteSpace(userId))
            {
                return new List<HackathonEntity>();
            }

            IEnumerable<HackathonEntity> hackathons = (await ListAllHackathonsAsync(cancellationToken)).Values;
            // filter by admin. PlatformAdmin can access every hackathon
            if (!ClaimsHelper.IsPlatformAdministrator(user))
            {
                List<HackathonEntity> filtered = new List<HackathonEntity>();
                foreach (var item in hackathons)
                {
                    if (item.Status == HackathonStatus.offline)
                        continue;

                    var admins = await HackathonAdminManagement.ListHackathonAdminAsync(item.Name, cancellationToken);
                    if (admins.Any(a => a.UserId == userId))
                    {
                        filtered.Add(item);
                    }
                }
                hackathons = filtered;
            }
            return hackathons;
        }

        private async Task<IEnumerable<HackathonEntity>> ListEnrolledHackathons(ClaimsPrincipal user, HackathonQueryOptions options, CancellationToken cancellationToken)
        {
            var result = new List<HackathonEntity>();

            string userId = ClaimsHelper.GetUserId(user);
            if (string.IsNullOrWhiteSpace(userId))
            {
                return result;
            }

            IEnumerable<HackathonEntity> hackathons = (await ListAllHackathonsAsync(cancellationToken)).Values;
            foreach (var hackathon in hackathons)
            {
                if (hackathon.Status == HackathonStatus.offline)
                    continue;

                var enrolled = await EnrollmentManagement.IsUserEnrolledAsync(hackathon, userId, cancellationToken);
                if (enrolled)
                {
                    result.Add(hackathon);
                }
            }
            return result;
        }
        private async Task<IEnumerable<HackathonEntity>> ListFreshHackathons(HackathonQueryOptions options, CancellationToken cancellationToken)
        {
            IEnumerable<HackathonEntity> hackathons = (await ListAllHackathonsAsync(cancellationToken)).Values;

            hackathons = hackathons.Where(
                h => h.EventStartedAt.GetValueOrDefault().ToUniversalTime() > DateTime.UtcNow
                && h.Status == HackathonStatus.online);
            return hackathons;
        }

        public async Task<IEnumerable<HackathonEntity>> ListPaginatedHackathonsAsync(ClaimsPrincipal user, HackathonQueryOptions options, CancellationToken cancellationToken = default)
        {
            IEnumerable<HackathonEntity> hackathons = new List<HackathonEntity>();
            // get candidates
            HackathonListType listType = options.ListType.GetValueOrDefault(HackathonListType.online);
            switch (listType)
            {
                case HackathonListType.online:
                    hackathons = await ListOnlineHackathons(options, cancellationToken);
                    break;
                case HackathonListType.admin:
                    hackathons = await ListAdminHackathons(user, options, cancellationToken);
                    break;
                case HackathonListType.enrolled:
                    hackathons = await ListEnrolledHackathons(user, options, cancellationToken);
                    break;
                case HackathonListType.fresh:
                    hackathons = await ListFreshHackathons(options, cancellationToken);
                    break;
                default:
                    break;
            }

            // search
            if (!string.IsNullOrWhiteSpace(options.Search))
            {
                hackathons = hackathons.Where(h => h.Name.Contains(options.Search, StringComparison.OrdinalIgnoreCase)
                                                || (h.DisplayName?.Contains(options.Search, StringComparison.OrdinalIgnoreCase)).GetValueOrDefault(false)
                                                || (h.Detail?.Contains(options.Search, StringComparison.OrdinalIgnoreCase)).GetValueOrDefault(false));
            }

            // ordering and paging
            return OrderAndPaging(options, hackathons);
        }
        #endregion

        #region GetHackathonRolesAsync
        public async Task<HackathonRoles> GetHackathonRolesAsync(HackathonEntity hackathon, ClaimsPrincipal user, CancellationToken cancellationToken = default)
        {
            string userId = ClaimsHelper.GetUserId(user);
            if (hackathon == null || string.IsNullOrEmpty(userId))
            {
                // no roles for anonymous user
                return null;
            }

            bool isAdmin = false, isEnrolled = false, isJudge = false;
            // admin
            if (ClaimsHelper.IsPlatformAdministrator(user))
            {
                isAdmin = true;
            }
            else
            {
                var admins = await HackathonAdminManagement.ListHackathonAdminAsync(hackathon.Name, cancellationToken);
                isAdmin = admins.Any(a => a.UserId == userId);
            }

            // enrollment
            isEnrolled = await EnrollmentManagement.IsUserEnrolledAsync(hackathon, userId, cancellationToken);

            // judge
            isJudge = await JudgeManagement.IsJudgeAsync(hackathon.Name, userId, cancellationToken);

            return new HackathonRoles
            {
                isAdmin = isAdmin,
                isEnrolled = isEnrolled,
                isJudge = isJudge
            };
        }
        #endregion

        #region ListAllHackathonsAsync
        public async Task<Dictionary<string, HackathonEntity>> ListAllHackathonsAsync(CancellationToken cancellationToken = default)
        {
            return await Cache.GetOrAddAsync(cacheKeyForAllHackathon,
                TimeSpan.FromHours(1),
                (token) =>
                {
                    return StorageContext.HackathonTable.ListAllHackathonsAsync(token);
                }, true, cancellationToken);
        }
        #endregion

        #region ListHackathonRolesAsync
        public async Task<IEnumerable<Tuple<HackathonEntity, HackathonRoles>>> ListHackathonRolesAsync(IEnumerable<HackathonEntity> hackathons, ClaimsPrincipal user, CancellationToken cancellationToken = default)
        {
            List<Tuple<HackathonEntity, HackathonRoles>> tuples = new List<Tuple<HackathonEntity, HackathonRoles>>();
            foreach (var hackathon in hackathons)
            {
                var roles = await GetHackathonRolesAsync(hackathon, user, cancellationToken);
                tuples.Add(Tuple.Create(hackathon, roles));
            }

            return tuples;
        }
        #endregion
    }
}
