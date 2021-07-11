using Authing.ApiClient.Auth;
using Authing.ApiClient.Types;
using Kaiyuanshe.OpenHackathon.Server.Auth;
using Kaiyuanshe.OpenHackathon.Server.Cache;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Security.Claims;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Biz
{
    public interface IUserManagement
    {
        /// <summary>
        /// Handle data from succesful Authing login.
        /// </summary>
        /// <param name="loginInfo">data from Authig</param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task AuthingAsync(UserInfo loginInfo, CancellationToken cancellationToken = default);

        /// <summary>
        /// Get User info from local table
        /// </summary>
        /// <param name="userId"></param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<UserInfo> GetUserByIdAsync(string userId, CancellationToken cancellationToken = default);

        /// <summary>
        /// Get User remotely from Authing
        /// </summary>
        /// <param name="userPoolId"></param>
        /// <param name="token"></param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<User> GetCurrentUserRemotelyAsync(string userPoolId, string token, CancellationToken cancellationToken = default);

        /// <summary>
        /// Get basic Claims of user associated with an Token. Return empty list if token is invalid.
        /// Resource-based claims are not included for performance reaons.
        /// </summary>
        /// <param name="token"></param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<IEnumerable<Claim>> GetUserBasicClaimsAsync(string token, CancellationToken cancellationToken = default);

        /// <summary>
        /// Get <seealso cref="UserTokenEntity"/> using AccessToken.
        /// </summary>
        /// <param name="token">AccessToken from Authing/Github</param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<UserTokenEntity> GetTokenEntityAsync(string token, CancellationToken cancellationToken = default);

        /// <summary>
        /// Validate AccessToken locally without calling Authing's API remotely.
        /// </summary>
        /// <param name="token">the token to validate</param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<ValidationResult> ValidateTokenAsync(string token, CancellationToken cancellationToken = default);

        /// <summary>
        /// Validate <see cref="UserTokenEntity"/> locally which contains an AccessToken/>
        /// </summary>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<ValidationResult> ValidateTokenAsync(UserTokenEntity tokenEntity, CancellationToken cancellationToken = default);

        /// <summary>
        /// Validate AccessToken by calling Authing Api
        /// </summary>
        /// <param name="userPoolId">Authing's user Pool Id</param>
        /// <param name="token">the Token to validate</param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<JWTTokenStatus> ValidateTokenRemotelyAsync(string userPoolId, string token, CancellationToken cancellationToken = default);
   }

    /// <inheritdoc cref="IUserManagement"/>
    public class UserManagement : ManagementClientBase, IUserManagement
    {
        public async Task AuthingAsync(UserInfo userInfo, CancellationToken cancellationToken = default)
        {
            userInfo.Id = userInfo.Id?.ToLower();
            await StorageContext.UserTable.SaveUserAsync(userInfo, cancellationToken);
            Cache.Remove(CacheKeys.GetCacheKey(CacheEntryType.User, userInfo.Id));

            // UserTokenEntity. 
            var userToken = new UserTokenEntity
            {
                PartitionKey = DigestHelper.SHA512Digest(userInfo.Token),
                RowKey = string.Empty,
                UserId = userInfo.Id,
                TokenExpiredAt = userInfo.TokenExpiredAt,
                Token = userInfo.Token,
                CreatedAt = DateTime.UtcNow,
            };
            await StorageContext.UserTokenTable.InsertOrReplaceAsync(userToken, cancellationToken);
        }

        public async Task<User> GetCurrentUserRemotelyAsync(string userPoolId, string token, CancellationToken cancellationToken = default)
        {
            if (string.IsNullOrWhiteSpace(userPoolId))
                throw new ArgumentNullException(string.Format(Resources.Parameter_Required, nameof(userPoolId)));
            if (string.IsNullOrWhiteSpace(token))
                throw new ArgumentNullException(string.Format(Resources.Parameter_Required, nameof(token)));

            var authenticationClient = new AuthenticationClient(userPoolId);
            return await authenticationClient.CurrentUser(token, cancellationToken);
        }

        public async Task<IEnumerable<Claim>> GetUserBasicClaimsAsync(string token, CancellationToken cancellationToken = default)
        {
            IList<Claim> claims = new List<Claim>();

            var tokenEntity = await GetTokenEntityAsync(token, cancellationToken);
            var tokenValidationResult = await ValidateTokenAsync(tokenEntity, cancellationToken);
            if (tokenValidationResult != ValidationResult.Success)
            {
                // token invalid
                return claims;
            }

            // User Id
            claims.Add(ClaimsHelper.UserId(tokenEntity.UserId));

            // PlatformAdministrator
            var pa = await GetPlatformAdminClaim(tokenEntity.UserId, cancellationToken);
            if (pa != null)
            {
                claims.Add(pa);
            }

            return claims;
        }

        public virtual async Task<UserTokenEntity> GetTokenEntityAsync(string token, CancellationToken cancellationToken = default)
        {
            string hash = DigestHelper.SHA512Digest(token);
            return await StorageContext.UserTokenTable.RetrieveAsync(hash, string.Empty, cancellationToken);
        }

        public async Task<ValidationResult> ValidateTokenAsync(string token, CancellationToken cancellationToken = default)
        {
            // the token must not be empty
            if (string.IsNullOrWhiteSpace(token))
                return new ValidationResult(Resources.Auth_Unauthorized);

            var tokenEntity = await GetTokenEntityAsync(token, cancellationToken);
            return await ValidateTokenAsync(tokenEntity, cancellationToken);
        }

        public Task<ValidationResult> ValidateTokenAsync(UserTokenEntity tokenEntity, CancellationToken cancellationToken = default)
        {
            // existence
            if (tokenEntity == null)
                return Task.FromResult(new ValidationResult(Resources.Auth_Unauthorized));

            // expiry
            if (tokenEntity.TokenExpiredAt < DateTime.UtcNow)
            {
                return Task.FromResult(new ValidationResult(string.Format(Resources.Auth_TokenExpired, tokenEntity.TokenExpiredAt.ToString("o"))));
            }

            return Task.FromResult(ValidationResult.Success);
        }

        public async Task<JWTTokenStatus> ValidateTokenRemotelyAsync(string userPoolId, string token, CancellationToken cancellationToken = default)
        {
            if (string.IsNullOrWhiteSpace(userPoolId))
                throw new ArgumentNullException(string.Format(Resources.Parameter_Required, nameof(userPoolId)));
            if (string.IsNullOrWhiteSpace(token))
                throw new ArgumentNullException(string.Format(Resources.Parameter_Required, nameof(token)));

            var authenticationClient = new AuthenticationClient(userPoolId);
            var jwtTokenStatus = await authenticationClient.CheckLoginStatus(token, cancellationToken);
            return jwtTokenStatus;
        }

        internal virtual async Task<Claim> GetPlatformAdminClaim(string userId, CancellationToken cancellationToken)
        {
            var admin = await StorageContext.HackathonAdminTable.GetPlatformRole(userId, cancellationToken);
            if (admin != null && admin.IsPlatformAdministrator())
            {
                return ClaimsHelper.PlatformAdministrator(userId);
            }

            return null;
        }

        #region GetUserByIdAsync
        public async Task<UserInfo> GetUserByIdAsync(string userId, CancellationToken cancellationToken = default)
        {
            if (string.IsNullOrWhiteSpace(userId))
                return null;

            return await Cache.GetOrAddAsync(
                CacheKeys.GetCacheKey(CacheEntryType.User, userId),
                TimeSpan.FromHours(6),
                ct => StorageContext.UserTable.GetUserByIdAsync(userId, ct),
                true,
                cancellationToken);
        }
        #endregion
    }
}
