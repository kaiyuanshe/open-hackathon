using Authing.ApiClient.Types;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Models
{
    /// <summary>
    /// User info. Added for better Swagger doc. Exactly the same as <seealso cref="User"/>
    /// </summary>
    public class UserInfo : ModelBase
    {
        /// <summary>
        /// name of user. Unique within pool. Required
        /// </summary>
        /// <example>zhangsan</example>
        [MaxLength(512)]
        [JsonProperty("name")]
        public string Name { get; set; }

        /// <summary>
        /// Given name.
        /// </summary>
        /// <example>San</example>
        [MaxLength(256)]
        [JsonProperty("givenName")]
        public string GivenName { get; set; }

        /// <summary>
        /// Family name
        /// </summary>
        /// <example>Zhang</example>
        [MaxLength(256)]
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
        /// Profile
        /// </summary>
        [MaxLength(10240)]
        [JsonProperty("profile")]
        public string Profile { get; set; }

        /// <summary>
        /// preferred Username
        /// </summary>
        [JsonProperty("preferredUsername")]
        [MaxLength(512)]
        public string PreferredUsername { get; set; }

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
        [MaxLength(128)]
        [JsonProperty("birthdate")]
        public string Birthdate { get; set; }

        /// <summary>
        /// Zone info
        /// </summary>
        /// <example>GMT+8</example>
        [JsonProperty("zoneinfo")]
        [MaxLength(256)]
        public string Zoneinfo { get; set; }

        /// <summary>
        /// Company name
        /// </summary>
        /// <example>Contoso Inc.</example>
        [MaxLength(128)]
        [JsonProperty("company")]
        public string Company { get; set; }

        /// <summary>
        /// locale info
        /// </summary>
        /// <example>zh-CN</example>
        [JsonProperty("locale")]
        [MaxLength(128)]
        public string Locale { get; set; }

        [JsonProperty("formatted")]
        public string Formatted { get; set; }

        /// <summary>
        /// Street address
        /// </summary>
        /// <example>One Street</example>
        [JsonProperty("streetAddress")]
        public string StreetAddress { get; set; }

        /// <summary>
        /// Locality
        /// </summary>
        /// <example>No 999</example>
        [JsonProperty("locality")]
        public string Locality { get; set; }

        /// <summary>
        /// Region of the address
        /// </summary>
        /// <example>Tianfu new district</example>
        [MaxLength(64)]
        [JsonProperty("region")]
        public string Region { get; set; }

        /// <summary>
        /// postal code
        /// </summary>
        /// <example>637700</example>
        [MaxLength(32)]
        [JsonProperty("postalCode")]
        public string PostalCode { get; set; }

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

        /// <summary>
        /// address where user lives
        /// </summary>
        /// <example>Room 111, No 1, Road ABC, District DEF, Chengdu, Sichuan, China</example>
        [MaxLength(512)]
        [JsonProperty("address")]
        public string Address { get; set; }


        /// <summary>
        /// Browser infomation of last login
        /// </summary>
        /// <example>Chrome</example>
        [MaxLength(128)]
        [JsonProperty("browser")]
        public string Browser { get; set; }

        /// <summary>
        /// Device of login
        /// </summary>
        [JsonProperty("device")]
        [MaxLength(256)]
        public string Device { get; set; }

        /// <summary>
        /// Whether or not the user is soft-deleted.
        /// </summary>
        /// <example>false</example>
        [JsonProperty("isDeleted")]
        public bool? IsDeleted { get; set; }

        /// <summary>
        /// id(from Authing). Globally unique. Reqired.
        /// </summary>
        /// <example>1</example>
        [Required]
        [MaxLength(128)]
        [JsonProperty("id")]
        public string Id { get; set; }

        /// <summary>
        /// ARN
        /// </summary>
        [JsonProperty("arn")]
        public string Arn { get; set; }

        /// <summary>
        /// Pool Id of Authing. Empty if not login with Authing
        /// </summary>
        /// <example>1eab1111d1a111d11c111c11</example>
        [MaxLength(64)]
        [JsonProperty("userPoolId")]
        [Required]
        public string UserPoolId { get; set; }

        /// <summary>
        /// User name
        /// </summary>
        [JsonProperty("username")]
        [MaxLength(1024)]
        public string Username { get; set; }

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
        /// Union Id
        /// </summary>
        /// <example>8814383</example>
        [JsonProperty("unionid")]
        public string Unionid { get; set; }

        /// <summary>
        /// Id from OAuth Provider. e.g. Id of Github. Empty if not login with oauth(social login)
        /// </summary>
        /// <example>8814383</example>
        [MaxLength(128)]
        [JsonProperty("openId")]
        public string OpenId { get; set; }

        /// <summary>
        /// Identities
        /// </summary>
        [JsonProperty("identities")]
        public IEnumerable<Identity> Identities { get; set; }

        /// <summary>
        /// Nick name of an user, usually for display.
        /// </summary>
        /// <example>San Zhang</example>
        [MaxLength(128)]
        //[Required]
        [JsonProperty("nickName")]
        public string Nickname { get; set; }

        /// <summary>
        /// Registration Source
        /// </summary>
        /// <example>["social:github"]</example>
        [JsonProperty("registerSource")]
        public IEnumerable<string> RegisterSource { get; set; }

        /// <summary>
        /// address of avatar. Not required. If not empty, must be a valid Url.
        /// </summary>
        /// <example>https://contoso.com/images/avatar/zhangsan.jpg</example>
        [JsonProperty("photo")]
        [Url]
        [MaxLength(1024)]
        public string Photo { get; set; }

        /// <summary>
        /// Password
        /// </summary>
        [JsonProperty("password")]
        public string Password { get; set; }

        /// <summary>
        /// Detailed response from social login.
        /// </summary>
        /// <example>{"login":"zhangsan","id":1,"avatar_url":"https://avatars.githubusercontent.com/u/1?v=4","type":"User","site_admin":false,"name":"Zhang San","location":"Shanghai China","email":"zhangsan@contoso.com"}</example>
        [MaxLength(10240)]
        [JsonProperty("oauth")]
        public string OAuth { get; set; }

        /// <summary>
        /// Token from Authing/Github, which can be used to call Authing/Github's rest API
        /// </summary>
        /// <example>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1ZWM3OGEyMGY4MjE2ZDRiNGEwYjQ3MjEi...</example>
        [Required]
        [MinLength(1)]
        [MaxLength(10240)]
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
        [JsonProperty("lastLogin")]
        public string LastLogin { get; set; }

        /// <summary>
        /// Ip address of last login.
        /// </summary>
        /// <example>10.0.0.1</example>
        [MaxLength(128)]
        [JsonProperty("lastIp")]
        public string LastIp { get; set; }

        /// <summary>
        /// Timestamp when the user account was created
        /// </summary>
        /// <example>2008-01-14T04:33:35Z</example>
        [JsonProperty("signedUp")]
        public string SignedUp { get; set; }

        /// <summary>
        /// Whether or not the user is blocked.
        /// </summary>
        /// <example>false</example>
        [JsonProperty("blocked")]
        public bool? Blocked { get; set; }

        ///// <summary>
        ///// Roles
        ///// </summary>
        //[JsonProperty("roles")]
        //public PaginatedRoles Roles { get; set; }

        ///// <summary>
        ///// Groups
        ///// </summary>
        //[JsonProperty("groups")]
        //public PaginatedGroups Groups { get; set; }
    }
}
