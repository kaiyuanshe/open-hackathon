using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Helpers;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Authing.ApiClient.Types;
using Authing.ApiClient.Auth;

namespace Kaiyuanshe.OpenHackathon.Server.Biz
{
    public interface ILoginManager
    {
        Task<JWTTokenStatus> ValidateAccessTokenAsync(string userPoolId, string accessToken, CancellationToken cancellationToken = default);
        Task<UserEntity> AuthingAsync(UserLoginInfo loginInfo, CancellationToken cancellationToken = default);
        Task<UserTokenEntity> GetTokenEntityAsync(string token, CancellationToken cancellationToken = default);
    }

    public class LoginManager : ManagerBase, ILoginManager
    {
        public async Task<UserEntity> AuthingAsync(UserLoginInfo loginInfo, CancellationToken cancellationToken = default)
        {
            var existing = await StorageContext.UserTable.RetrieveAsync(loginInfo.Id, string.Empty, cancellationToken);
            // UserEntity
            if (existing != null)
            {
                #region properties
                // some info can be overriden in OPH, so only update those empty fields during authing login
                if (string.IsNullOrWhiteSpace(existing.Address))
                    existing.Address = loginInfo.Address;
                if (string.IsNullOrWhiteSpace(existing.Avatar))
                    existing.Avatar = loginInfo.Avatar;
                if (string.IsNullOrWhiteSpace(existing.Birthdate))
                    existing.Birthdate = loginInfo.Birthdate;
                if (!existing.Blocked.HasValue)
                    existing.Blocked = loginInfo.Blocked;
                if (string.IsNullOrWhiteSpace(existing.City))
                    existing.City = loginInfo.City;
                if (string.IsNullOrWhiteSpace(existing.Company))
                    existing.Company = loginInfo.Company;
                if (string.IsNullOrWhiteSpace(existing.Country))
                    existing.Country = loginInfo.Country;
                if (string.IsNullOrWhiteSpace(existing.FamilyName))
                    existing.FamilyName = loginInfo.FamilyName;
                if (string.IsNullOrWhiteSpace(existing.Gender))
                    existing.Gender = loginInfo.Gender;
                if (string.IsNullOrWhiteSpace(existing.GivenName))
                    existing.GivenName = loginInfo.GivenName;
                if (!existing.IsDeleted.HasValue)
                    existing.IsDeleted = loginInfo.IsDeleted;
                if (string.IsNullOrWhiteSpace(existing.MiddleName))
                    existing.MiddleName = loginInfo.MiddleName;
                if (string.IsNullOrWhiteSpace(existing.Nickname))
                    existing.Nickname = loginInfo.Nickname;
                if (string.IsNullOrWhiteSpace(existing.PostalCode))
                    existing.PostalCode = loginInfo.PostalCode;
                if (string.IsNullOrWhiteSpace(existing.Province))
                    existing.Province = loginInfo.Province;
                if (string.IsNullOrWhiteSpace(existing.Region))
                    existing.Region = loginInfo.Region;
                if (string.IsNullOrWhiteSpace(existing.UserName))
                    existing.UserName = loginInfo.UserName;
                if (string.IsNullOrWhiteSpace(existing.Website))
                    existing.Website = loginInfo.Website;

                // login related info, update it always in each login
                existing.Browser = loginInfo.Browser ?? existing.Browser;
                existing.LastIp = loginInfo.LastIp ?? existing.LastIp;
                existing.LastLoginTime = loginInfo.LastLoginTime.HasValue ? loginInfo.LastLoginTime.Value : DateTime.UtcNow;
                existing.LoginsCount = loginInfo.LoginsCount.HasValue ? loginInfo.LoginsCount.Value : (existing.LoginsCount.GetValueOrDefault(0) + 1);
                existing.OAuth = loginInfo.OAuth;
                existing.OpenId = loginInfo.OpenId;
                existing.SignedUpDate = loginInfo.SignedUpDate;
                existing.UserPoolId = loginInfo.UserPoolId;

                // OPH cannot verify email/phone, so if needs update email, go to authing or github
                existing.Email = loginInfo.Email;
                existing.EmailVerified = loginInfo.EmailVerified;
                existing.Phone = loginInfo.Phone;
                existing.PhoneVerified = loginInfo.PhoneVerified;
                #endregion
                await StorageContext.UserTable.MergeAsync(existing, cancellationToken);
            }
            else
            {
                #region new entity
                existing = new UserEntity
                {
                    PartitionKey = loginInfo.Id,
                    RowKey = string.Empty,
                    Address = loginInfo.Address,
                    Avatar = loginInfo.Avatar,
                    Blocked = loginInfo.Blocked,
                    Birthdate = loginInfo.Birthdate,
                    Browser = loginInfo.Browser,
                    City = loginInfo.City,
                    Company = loginInfo.Company,
                    Country = loginInfo.Country,
                    Email = loginInfo.Email,
                    EmailVerified = loginInfo.EmailVerified,
                    FamilyName = loginInfo.FamilyName,
                    Gender = loginInfo.Gender,
                    GivenName = loginInfo.GivenName,
                    LastIp = loginInfo.LastIp,
                    IsDeleted = loginInfo.IsDeleted,
                    LastLoginTime = loginInfo.LastLoginTime.GetValueOrDefault(DateTime.UtcNow),
                    LoginsCount = loginInfo.LoginsCount.GetValueOrDefault(1),
                    MiddleName = loginInfo.MiddleName,
                    Nickname = loginInfo.Nickname,
                    OAuth = loginInfo.OAuth,
                    OpenId = loginInfo.OpenId,
                    Phone = loginInfo.Phone,
                    PhoneVerified = loginInfo.PhoneVerified,
                    PostalCode = loginInfo.PostalCode,
                    Region = loginInfo.Region,
                    Province = loginInfo.Province,
                    SignedUpDate = loginInfo.SignedUpDate,
                    UserName = loginInfo.UserName,
                    UserPoolId = loginInfo.UserPoolId,
                    Website = loginInfo.Website,
                };
                #endregion
                await StorageContext.UserTable.InsertAsync(existing, cancellationToken);
            }

            // UserTokenEntity. 
            var userToken = new UserTokenEntity
            {
                PartitionKey = DigestHelper.SHA512Digest(loginInfo.Token),
                RowKey = string.Empty,
                UserId = loginInfo.Id,
                TokenExpiredAt = loginInfo.TokenExpiredAt,
                Token = loginInfo.Token,
            };
            await StorageContext.UserTokenTable.InsertOrReplaceAsync(userToken, cancellationToken);

            return await StorageContext.UserTable.RetrieveAsync(loginInfo.Id, string.Empty, cancellationToken);
        }

        public async Task<JWTTokenStatus> ValidateAccessTokenAsync(string userPoolId, string accessToken, CancellationToken cancellationToken = default)
        {
            if (string.IsNullOrWhiteSpace(userPoolId))
                throw new ArgumentNullException("userPoolId is null or empty");
            if (string.IsNullOrWhiteSpace(accessToken))
                throw new ArgumentNullException("accessToken is null or empty");

            var authenticationClient = new AuthenticationClient(userPoolId);
            var jwtTokenStatus = await authenticationClient.CheckLoginStatus(accessToken, cancellationToken);
            return jwtTokenStatus;
        }

        public async Task<UserTokenEntity> GetTokenEntityAsync(string token, CancellationToken cancellationToken = default)
        {
            string hash = DigestHelper.SHA512Digest(token);
            return await StorageContext.UserTokenTable.RetrieveAsync(hash, string.Empty, cancellationToken);
        }
    }
}
