using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.Entities
{
    /// <summary>
    /// Entity for User
    /// 
    /// PartitionKey: id(from Authing). Globally unique.
    /// RowKey: String.Empty
    /// </summary>
    public class UserEntity : AdvancedTableEntity
    {
        public string Id
        {
            get
            {
                return PartitionKey;
            }
        }

        /// <summary>
        /// Pool Id of Authing. Empty if not login with Authing
        /// </summary>
        public string UserPoolId { get; set; }

        /// <summary>
        /// Unique within pool.
        /// </summary>
        public string UserName { get; set; }

        public string Nickname { get; set; }

        public string Email { get; set; }

        public bool? EmailVerified { get; set; }

        public string Phone { get; set; }

        public bool? PhoneVerified { get; set; }

        /// <summary>
        /// Id from OAuth Provider. e.g. Id of Github. Empty if not login with oauth(social login)
        /// </summary>
        public string OpenId { get; set; }

        /// <summary>
        /// OAuth provider. e.g. github. empty if not social login
        /// </summary>
        public string OAuth { get; set; }

        public string Avatar { get; set; }

        public int? LoginsCount { get; set; }

        public DateTime? LastLoginTime { get; set; }

        public string LastIp { get; set; }

        public string Browser { get; set; }

        public DateTime? SignedUpDate { get; set; }

        public bool? Blocked { get; set; }

        public bool? IsDeleted { get; set; }

        public string GivenName { get; set; }

        public string FamilyName { get; set; }

        public string MiddleName { get; set; }

        public string Company { get; set; }

        public string Profile { get; set; }

        public string Website { get; set; }

        public string Gender { get; set; }

        public string Birthdate { get; set; }

        public string Address { get; set; }

        public string PostalCode { get; set; }

        public string Region { get; set; }

        public string City { get; set; }

        public string Province { get; set; }

        public string Country { get; set; }

        public DateTime? CreatedAt { get; set; }
    }
}
