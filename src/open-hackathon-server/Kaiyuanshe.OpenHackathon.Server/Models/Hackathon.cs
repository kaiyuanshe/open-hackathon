using Kaiyuanshe.OpenHackathon.Server.Models.Validations;
using System;
using System.ComponentModel.DataAnnotations;

namespace Kaiyuanshe.OpenHackathon.Server.Models
{
    /// <summary>
    /// Represents a hackathon
    /// </summary>
    public class Hackathon : ModelBase
    {
        /// <summary>
        /// Name of a hackathon. Can only be set when it's created. Readonly afterwards.
        /// Length between 1-100. alphabeta and numbers only.
        /// </summary>
        /// <example>foo</example>
        public string name { get; internal set; }

        /// <summary>
        /// Name for display only.
        /// </summary>
        /// <example>Hackathon ABC - 2020</example>
        [MinLength(1)]
        [MaxLength(256)]
        public string displayName { get; set; }

        /// <summary>
        /// A short sentence for advertisement.
        /// </summary>
        /// <example>Let's Hack!</example>
        [MaxLength(256)]
        public string ribbon { get; set; }

        /// <summary>
        /// Summary or short description. 
        /// </summary>
        /// <example>Let's Hack for ABC - a summary</example>
        [MaxLength(512)]
        public string summary { get; set; }

        /// <summary>
        /// Detailed description. Usually rich-text html. Max length is 64K. 
        /// If it contains utf-18 or unicode, the max length is 32K.
        /// </summary>
        /// <example>A detailed rich-text html to desribe the hackathon in detail</example>
        [MaxLength(65535)]
        public string detail { get; set; }

        /// <summary>
        /// An address where the hackathon is held. Can be used to show a navigation map. Leave it empty if online.
        /// </summary>
        /// <example>Shanghai, China</example>
        [MaxLength(256)]
        public string location { get; set; }

        /// <summary>
        /// A list of banner images. At least 1 image. Max 10 images supported. All images must be invalid Uri.
        /// To add a new picture, be sure to submit all pictures in request including the existing ones. 
        /// The entire list will be replaced with list in request.
        /// </summary>
        [HackathonBannersPolicy]
        public PictureInfo[] banners { get; set; }

        /// <summary>
        /// whether a hackathon is readOnly or not. 
        /// If a hackathon is readOnly, no WRITE operation is allowed including hackathon, enrollment, team etc.
        /// </summary>
        /// <example>false</example>
        public bool readOnly { get; internal set; }

        /// <summary>
        /// Status of Hackathon. Readonly. Can be updated though status change APIs like approve, delete.
        /// </summary>
        /// <example>online</example>
        public HackathonStatus status { get; internal set; }

        /// <summary>
        /// Id of the user who creates the Hackathon. ReadOnly.
        /// </summary>
        /// <example>1</example>
        public string creatorId { get; internal set; }

        /// <summary>
        /// Number of enrolled users. Only approved enrollments are counted.
        /// </summary>
        /// <example>100</example>
        public int enrollment { get; set; }

        /// <summary>
        /// Maximum users allowed to enroll this hackathon. 0 means unlimited. default value: 0.
        /// </summary>
        /// <example>1000</example>
        [Range(0, 100_000)]
        public int? maxEnrollment { get; set; }

        /// <summary>
        /// whether or not user registration needs admin's manual approval. default: false
        /// </summary>
        /// <example>false</example>
        public bool? autoApprove { get; set; }

        /// <summary>
        /// tags. An array of any string. At most 20 tags.
        /// </summary>
        /// <example>tag1</example>
        [MaxLength(20)]
        public string[] tags { get; set; }

        /// <summary>
        /// The timestamp when the hackathon starts.
        /// </summary>
        /// <example>2008-01-14T04:33:35Z</example>
        public DateTime? eventStartedAt { get; set; }

        /// <summary>
        /// The timestamp when the hackathon ends
        /// </summary>
        public DateTime? eventEndedAt { get; set; }

        /// <summary>
        /// The timestamp when the hackathon begins to accept user enrollement.
        /// </summary>
        /// <example>2008-01-14T04:33:35Z</example>
        public DateTime? enrollmentStartedAt { get; set; }

        /// <summary>
        /// The timestamp when the hackathon stops accepting user enrollement
        /// </summary>
        /// <example>2008-01-14T04:33:35Z</example>
        public DateTime? enrollmentEndedAt { get; set; }

        /// <summary>
        /// The timestamp when the judges begin to review and rate the output showed/uploaded by enrolled users
        /// </summary>
        /// <example>2008-01-14T04:33:35Z</example>
        public DateTime? judgeStartedAt { get; set; }

        /// <summary>
        /// The timestamp when the reviews/ratings should be completed.
        /// </summary>
        /// <example>2008-01-14T04:33:35Z</example>
        public DateTime? judgeEndedAt { get; set; }

        /// <summary>
        /// roles of current user. null if anonymous.
        /// </summary>
        public HackathonRoles roles { get; internal set; }
    }

    /// <summary>
    /// Represents the role of current user
    /// </summary>
    public class HackathonRoles
    {
        /// <summary>
        /// whether current user is admin of hackathon.
        /// </summary>
        /// <example>true</example>
        public bool isAdmin { get; internal set; }

        /// <summary>
        /// whether current user is judge of hackathon.
        /// </summary>
        /// <example>true</example>
        public bool isJudge { get; internal set; }

        /// <summary>
        /// whether current user enrolled as contestant.
        /// </summary>
        /// <example>true</example>
        public bool isEnrolled { get; internal set; }
    }

    /// <summary>
    /// Represents a list of hackathon
    /// </summary>
    public class HackathonList : ResourceList<Hackathon>
    {
        /// <summary>
        /// List of hackathon
        /// </summary>
        public override Hackathon[] value { get; set; }
    }

    /// <summary>
    /// Status of Hackathon
    /// </summary>
    public enum HackathonStatus
    {
        /// <summary>
        /// the hackathon is in planning, a.k.a draft stage. Only visible to hackathon admins.
        /// </summary>
        planning,
        /// <summary>
        /// a request to make hackathon online is sent, and the request is not approved yet. Only visible to hackahton admins.
        /// </summary>
        pendingApproval,
        /// <summary>
        /// Online. visible to everyone.
        /// </summary>
        online,
        /// <summary>
        /// The hackathon is marked as Deleted. Only visible to platform admin.
        /// </summary>
        offline
    }

    /// <summary>
    /// ordering while list hackathons
    /// </summary>
    public enum HackathonOrderBy
    {
        /// <summary>
        /// order by createdAt
        /// </summary>
        createdAt,
        /// <summary>
        /// order by updatedAt
        /// </summary>
        updatedAt,
        /// <summary>
        /// order by hot
        /// </summary>
        hot,
    }

    /// <summary>
    /// type to list hackathons
    /// </summary>
    public enum HackathonListType
    {
        /// <summary>
        /// online hackathons.
        /// </summary>
        online,
        /// <summary>
        /// hackathons with admin access
        /// </summary>
        admin,
        ///// <summary>
        ///// enrolled hackathons
        ///// </summary>
        enrolled,
        /// <summary>
        /// hackathons about to start
        /// </summary>
        fresh,
    }
}
