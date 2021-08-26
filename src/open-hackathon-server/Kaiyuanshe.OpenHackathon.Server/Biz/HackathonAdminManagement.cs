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
    public interface IHackathonAdminManagement
    {
        /// <summary>
        ///  create a new hackathon admin
        /// </summary>
        /// <param name="admin"></param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<HackathonAdminEntity> CreateAdminAsync(HackathonAdmin admin, CancellationToken cancellationToken = default);

        /// <summary>
        /// List all Administrators of a Hackathon. PlatformAdministrator is not included.
        /// </summary>
        /// <param name="hackathonName">name of Hackathon</param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<IEnumerable<HackathonAdminEntity>> ListHackathonAdminAsync(string hackathonName, CancellationToken cancellationToken = default);
        Task<IEnumerable<HackathonAdminEntity>> ListPaginatedHackathonAdminAsync(string hackathonName, AdminQueryOptions options, CancellationToken cancellationToken = default);
        Task<HackathonAdminEntity> GetAdminAsync(string hackathonName, string userId, CancellationToken cancellationToken);
        Task DeleteAdminAsync(string hackathonName, string userId, CancellationToken cancellationToken);
        Task<bool> IsHackathonAdmin(string hackathonName, ClaimsPrincipal user, CancellationToken cancellationToken = default);
    }

    public class HackathonAdminManagement : ManagementClientBase, IHackathonAdminManagement
    {
        private readonly ILogger logger;

        public HackathonAdminManagement(ILogger<HackathonAdminManagement> logger)
        {
            this.logger = logger;
        }

        #region cache

        private void InvalidateAdminCache(string hackathonName)
        {
            string cacheKey = CacheKeys.GetCacheKey(CacheEntryType.HackathonAdmin, hackathonName);
            Cache.Remove(cacheKey);
        }

        #endregion

        #region CreateAdminAsync
        public async Task<HackathonAdminEntity> CreateAdminAsync(HackathonAdmin admin, CancellationToken cancellationToken = default)
        {
            HackathonAdminEntity entity = new HackathonAdminEntity
            {
                PartitionKey = admin.hackathonName,
                RowKey = admin.userId,
                CreatedAt = DateTime.UtcNow,
            };
            await StorageContext.HackathonAdminTable.InsertOrMergeAsync(entity, cancellationToken);

            InvalidateAdminCache(admin.hackathonName);
            return entity;
        }
        #endregion

        #region ListHackathonAdminAsync
        public async Task<IEnumerable<HackathonAdminEntity>> ListHackathonAdminAsync(string hackathonName, CancellationToken cancellationToken = default)
        {
            string cacheKey = CacheKeys.GetCacheKey(CacheEntryType.HackathonAdmin, hackathonName);
            return await Cache.GetOrAddAsync(cacheKey,
                TimeSpan.FromHours(1),
                (token) =>
                {
                    return StorageContext.HackathonAdminTable.ListByHackathonAsync(hackathonName, token);
                }, true, cancellationToken);
        }
        #endregion

        #region Task<IEnumerable<HackathonAdminEntity>> ListPaginatedHackathonAdminAsync(string hackathonName, AdminQueryOptions options, CancellationToken cancellationToken = default)
        public async Task<IEnumerable<HackathonAdminEntity>> ListPaginatedHackathonAdminAsync(string hackathonName, AdminQueryOptions options, CancellationToken cancellationToken = default)
        {
            IEnumerable<HackathonAdminEntity> allAdmins = await ListHackathonAdminAsync(hackathonName, cancellationToken);

            // paging
            int.TryParse(options.TableContinuationToken?.NextPartitionKey, out int np);
            int top = options.Top.GetValueOrDefault(100);
            var admins = allAdmins.OrderByDescending(a => a.CreatedAt).Skip(np).Take(top);

            // next paging
            options.Next = null;
            if (np + top < allAdmins.Count())
            {
                options.Next = new TableContinuationToken
                {
                    NextPartitionKey = (np + top).ToString(),
                    NextRowKey = (np + top).ToString(),
                };
            }

            return admins;
        }
        #endregion

        #region Task<HackathonAdminEntity> GetAdminAsync(string hackathonName, string userId, CancellationToken cancellationToken)
        public async Task<HackathonAdminEntity> GetAdminAsync(string hackathonName, string userId, CancellationToken cancellationToken)
        {
            if (string.IsNullOrWhiteSpace(hackathonName) || string.IsNullOrWhiteSpace(userId))
            {
                return null;
            }

            return await StorageContext.HackathonAdminTable.RetrieveAsync(hackathonName, userId, cancellationToken);
        }
        #endregion

        #region Task DeleteAdminAsync(string hackathonName, string userId, CancellationToken cancellationToken)
        public async Task DeleteAdminAsync(string hackathonName, string userId, CancellationToken cancellationToken)
        {
            if (string.IsNullOrWhiteSpace(hackathonName) || string.IsNullOrWhiteSpace(userId))
                return;

            await StorageContext.HackathonAdminTable.DeleteAsync(hackathonName, userId, cancellationToken);
        }
        #endregion

        #region Task<bool> IsHackathonAdmin(string hackathonName, string userId, CancellationToken cancellationToken = default);
        public async Task<bool> IsHackathonAdmin(string hackathonName, ClaimsPrincipal user, CancellationToken cancellationToken = default)
        {
            string userId = ClaimsHelper.GetUserId(user);
            if (string.IsNullOrWhiteSpace(userId))
                return false;

            if (ClaimsHelper.IsPlatformAdministrator(user))
            {
                return true;
            }
            else
            {
                var admins = await ListHackathonAdminAsync(hackathonName, cancellationToken);
                return admins.Any(a => a.UserId == userId);
            }
        }
        #endregion
    }
}
