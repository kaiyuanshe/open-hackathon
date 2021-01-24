using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Models
{
    /// <summary>
    /// Parameters for login(currently only Authing)
    /// </summary>
    public class UserLoginInfo
    {
        /// <summary>
        /// id(from Authing). Globally unique. Reqired.
        /// </summary>
        /// <example>1</example>
        [Required]
        [MaxLength(128)]
        [JsonProperty("id")]
        public string Id { get; set; }

        /// <summary>
        /// Pool Id of Authing. Empty if not login with Authing
        /// </summary>
        /// <example>1eab1111d1a111d11c111c11</example>
        [MaxLength(64)]
        [JsonProperty("userPoolId")]
        public string UserPoolId { get; set; }

        /// <summary>
        /// name of user. Unique within pool. Required
        /// </summary>
        /// <example>zhangsan</example>
        [MaxLength(128)]
        [Required]
        [JsonProperty("userName")]
        public string UserName { get; set; }

        /// <summary>
        /// Nick name of an user, usually for display.
        /// </summary>
        /// <example>San Zhang</example>
        [MaxLength(128)]
        [Required]
        [JsonProperty("nickName")]
        public string Nickname { get; set; }

        /// <summary>
        /// Email address.
        /// </summary>
        /// <example>zhangsan@contoso.com</example>
        [EmailAddress]
        [MaxLength(256)]
        [JsonProperty("email")]
        public string Email { get; set; }

        /// <summary>
        /// Whether the Email address is verified
        /// </summary>
        /// <example>true</example>
        [JsonProperty("emailVerified")]
        public bool? EmailVerified { get; set; }

        /// <summary>
        /// Phone number.
        /// </summary>
        /// <example>021-12345678</example>
        [JsonProperty("phone")]
        [Phone]
        [MaxLength(128)]
        public string Phone { get; set; }

        /// <summary>
        /// Whether the phone number is verified
        /// </summary>
        /// <example>false</example>
        [JsonProperty("phoneVerified")]
        public bool? PhoneVerified { get; set; }

        /// <summary>
        /// Id from OAuth Provider. e.g. Id of Github. Empty if not login with oauth(social login)
        /// </summary>
        /// <example>1</example>
        [MaxLength(128)]
        [JsonProperty("openId")]
        public string OpenId { get; set; }

        /// <summary>
        /// Token from Authing/Github, which can be used to call Authing/Github's rest API
        /// </summary>
        /// <example>5199831f4dd3b79e7c5b7e0ebe75d67aa66e79d4</example>
        [Required]
        [MinLength(1)]
        [MaxLength(1024)]
        [JsonProperty("token")]
        public string Token { get; set; }

        /// <summary>
        /// A timestamp when the token will be expired
        /// </summary>
        /// <example>2028-01-14T04:33:35Z</example>
        [Required]
        [JsonProperty("tokenExpiredAt")]
        public DateTime TokenExpiredAt { get; set; }

        /// <summary>
        /// OAuth provider. e.g. github. empty if not social login
        /// </summary>
        [MaxLength(64)]
        [JsonProperty("oauth")]
        public string OAuth { get; set; }

        /// <summary>
        /// address of avatar. Not required. If not empty, must be a valid Url.
        /// </summary>
        /// <example>https://contoso.com/images/avatar/zhangsan.jpg</example>
        [Url]
        [MaxLength(1024)]
        [JsonProperty("avatar")]
        public string Avatar { get; set; }

        /// <summary>
        /// logins count of an user
        /// </summary>
        /// <example>10</example>
        [Range(1, int.MaxValue)]
        [JsonProperty("loginsCount")]
        public int? LoginsCount { get; set; }

        /// <summary>
        /// timestamp of the most recent login
        /// </summary>
        /// <example>2008-01-14T04:33:35Z</example>
        [JsonProperty("lastLoginTime")]
        public DateTime? LastLoginTime { get; set; }

        /// <summary>
        /// Ip address of last login.
        /// </summary>
        [MaxLength(128)]
        [JsonProperty("lastIp")]
        public string LastIp { get; set; }

        /// <summary>
        /// Browser infomation of last login
        /// </summary>
        [MaxLength(128)]
        [JsonProperty("browser")]
        public string Browser { get; set; }

        /// <summary>
        /// Timestamp when the user account was created
        /// </summary>
        /// <example>2008-01-14T04:33:35Z</example>
        [JsonProperty("signedUpDate")]
        public DateTime? SignedUpDate { get; set; }

        /// <summary>
        /// Whether or not the user is blocked.
        /// </summary>
        /// <example>false</example>
        [JsonProperty("blocked")]
        public bool? Blocked { get; set; }

        /// <summary>
        /// Whether or not the user is soft-deleted.
        /// </summary>
        /// <example>false</example>
        [JsonProperty("isDeleted")]
        public bool? IsDeleted { get; set; }

        /// <summary>
        /// Given name.
        /// </summary>
        /// <example>San</example>
        [MaxLength(128)]
        [JsonProperty("givenName")]
        public string GivenName { get; set; }

        /// <summary>
        /// Family name
        /// </summary>
        /// <example>Zhang</example>
        [MaxLength(128)]
        [JsonProperty("familyName")]
        public string FamilyName { get; set; }

        /// <summary>
        /// Middle name
        /// </summary>
        /// <example>John</example>
        [MaxLength(128)]
        [JsonProperty("middleName")]
        public string MiddleName { get; set; }

        /// <summary>
        /// Company name
        /// </summary>
        /// <example>Contoso Inc.</example>
        [MaxLength(128)]
        [JsonProperty("company")]
        public string Company { get; set; }

        /// <summary>
        /// Url of the user's or company's homepage
        /// </summary>
        /// <example>https://contoso.com</example>
        [MaxLength(1024)]
        [Url]
        [JsonProperty("website")]
        public string Website { get; set; }

        /// <summary>
        /// Gender
        /// </summary>
        /// <example>female</example>
        [MaxLength(64)]
        [JsonProperty("gender")]
        public string Gender { get; set; }

        /// <summary>
        /// Date of birth.
        /// </summary>
        /// <example>1980/11</example>
        [MaxLength(64)]
        [JsonProperty("birthdate")]
        public string Birthdate { get; set; }

        /// <summary>
        /// address where user lives
        /// </summary>
        /// <example>Room 111, No 1, Road ABC, District DEF, Chengdu, Sichuan, China</example>
        [MaxLength(512)]
        [JsonProperty("address")]
        public string Address { get; set; }

        /// <summary>
        /// postal code
        /// </summary>
        /// <example>637700</example>
        [MaxLength(32)]
        [JsonProperty("postalCode")]
        public string PostalCode { get; set; }

        /// <summary>
        /// Region of the address
        /// </summary>
        /// <example>Tianfu new district</example>
        [MaxLength(64)]
        [JsonProperty("region")]
        public string Region { get; set; }

        /// <summary>
        /// City of the address
        /// </summary>
        /// <example>Chengdu</example>
        [MaxLength(64)]
        [JsonProperty("city")]
        public string City { get; set; }

        /// <summary>
        /// Province of the address
        /// </summary>
        /// <example>Sichuan</example>
        [MaxLength(64)]
        [JsonProperty("province")]
        public string Province { get; set; }

        /// <summary>
        /// Country of the address
        /// </summary>
        /// <example>China</example>
        [MaxLength(64)]
        [JsonProperty("country")]
        public string Country { get; set; }
    }
}
