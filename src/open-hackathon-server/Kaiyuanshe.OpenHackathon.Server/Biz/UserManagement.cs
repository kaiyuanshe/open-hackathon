﻿using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Helpers;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Authing.ApiClient.Types;
using Authing.ApiClient.Auth;
using System.ComponentModel.DataAnnotations;
using Microsoft.WindowsAzure.Storage.Table;
using System.Security.Claims;

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
        /// Get User remotely from Authing
        /// </summary>
        /// <param name="userPoolId"></param>
        /// <param name="token"></param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<User> GetCurrentUserRemotelyAsync(string userPoolId, string token, CancellationToken cancellationToken = default);

        /// <summary>
        /// Get Claims of user associated with an AccessToken
        /// </summary>
        /// <param name="token"></param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<IEnumerable<Claim>> GetCurrentUserClaims(string token, CancellationToken cancellationToken = default);

        /// <summary>
        /// Get <see cref="UserTokenEntity" /> using AccessToken.
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

    public class UserManagement : ManagementClientBase, IUserManagement
    {
        public async Task AuthingAsync(UserInfo userInfo, CancellationToken cancellationToken = default)
        {
            await StorageContext.UserTable.SaveUserAsync(userInfo, cancellationToken);

            // UserTokenEntity. 
            var userToken = new UserTokenEntity
            {
                PartitionKey = DigestHelper.SHA512Digest(userInfo.Token),
                RowKey = string.Empty,
                UserId = userInfo.Id,
                TokenExpiredAt = userInfo.TokenExpiredAt,
                Token = userInfo.Token,
            };
            await StorageContext.UserTokenTable.InsertOrReplaceAsync(userToken, cancellationToken);
        }

        public async Task<User> GetCurrentUserRemotelyAsync(string userPoolId, string token, CancellationToken cancellationToken = default)
        {
            if (string.IsNullOrWhiteSpace(userPoolId))
                throw new ArgumentNullException("userPoolId is null or empty");
            if (string.IsNullOrWhiteSpace(token))
                throw new ArgumentNullException("accessToken is null or empty");

            var authenticationClient = new AuthenticationClient(userPoolId);
            return await authenticationClient.CurrentUser(token, cancellationToken);
        }

        public async Task<UserTokenEntity> GetTokenEntityAsync(string token, CancellationToken cancellationToken = default)
        {
            string hash = DigestHelper.SHA512Digest(token);
            return await StorageContext.UserTokenTable.RetrieveAsync(hash, string.Empty, cancellationToken);
        }

        public async Task<ValidationResult> ValidateTokenAsync(string token, CancellationToken cancellationToken = default)
        {
            // the token must not be empty
            if (string.IsNullOrWhiteSpace(token))
                return new ValidationResult(@"token is required. Please add it to Http Headers: Headers[""Authorization""]=token TOKEN");

            var tokenEntity = await GetTokenEntityAsync(token, cancellationToken);
            // existence
            if (tokenEntity == null)
                return new ValidationResult($"token doesn't exist: {token}");

            // expiry
            if (tokenEntity.TokenExpiredAt < DateTime.UtcNow)
            {
                return new ValidationResult($"token expired, please login: {token}");
            }

            return ValidationResult.Success;
        }

        public async Task<JWTTokenStatus> ValidateTokenRemotelyAsync(string userPoolId, string token, CancellationToken cancellationToken = default)
        {
            if (string.IsNullOrWhiteSpace(userPoolId))
                throw new ArgumentNullException("userPoolId is null or empty");
            if (string.IsNullOrWhiteSpace(token))
                throw new ArgumentNullException("accessToken is null or empty");

            var authenticationClient = new AuthenticationClient(userPoolId);
            var jwtTokenStatus = await authenticationClient.CheckLoginStatus(token, cancellationToken);
            return jwtTokenStatus;
        }
    }
}
