using Kaiyuanshe.OpenHackathon.Server.Models.Enums;
using Kaiyuanshe.OpenHackathon.Server.Models.Validations;
using Newtonsoft.Json;
using System;
using System.ComponentModel.DataAnnotations;

namespace Kaiyuanshe.OpenHackathon.Server.Models
{
    /// <summary>
    /// Represents a hackathon
    /// </summary>
    public class Hackathon
    {
        /// <summary>
        /// Readonly unique Id of a Hackathon. Auto-generated in server side.
        /// </summary>
        [JsonProperty("id")]
        public string Id { get; internal set; }

        /// <summary>
        /// Name of a hackathon. Required. Length between 1-100
        /// </summary>
        [Required]
        [StringLength(100, MinimumLength = 1)]
        [JsonProperty("name")]
        public string Name { get; set; }

        /// <summary>
        /// A short sentence for advertisement. Max Length is 100.
        /// </summary>
        [MaxLength(100)]
        [JsonProperty("ribbon")]
        public string Ribbon { get; set; }

        /// <summary>
        /// Summary or short description. Max Length is 200.
        /// </summary>
        [MaxLength(200)]
        [JsonProperty("summary")]
        public string Summary { get; set; }

        /// <summary>
        /// Detailed description. Usually rich-text html. Required. Max length is 64K.
        /// </summary>
        [Required]
        [MaxLength(65535)]
        [JsonProperty("description")]
        public string Description { get; set; }

        /// <summary>
        /// An address where the hackathon is held. Can be used to show a navigation map. Leave it empty if online. Max Length is 100.
        /// </summary>
        [MaxLength(100)]
        [JsonProperty("location")]
        public string Location { get; set; }

        /// <summary>
        /// A list of banner images. At least 1 image. Max 10 images supported. All images must be invalid Uri.
        /// </summary>
        [Required]
        [HackathonBannersPolicy]
        [JsonProperty("banners")]
        public string[] Banners { get; set; }

        /// <summary>
        /// Status of Hackathon. Readonly. Can be updated though other API
        /// </summary>
        [JsonProperty("status")]
        public HackathonStatus Status { get; internal set; }

        /// <summary>
        /// Id of the user who creates the Hackathon. ReadOnly.
        /// </summary>
        [JsonProperty("creator_id")]
        public string CreatorId { get; internal set; }

        /// <summary>
        /// Maximum uses allowed to enroll this hackathon. Required.
        /// </summary>
        [Range(1, int.MaxValue)]
        [JsonProperty("max_enrollment")]
        public int MaxEnrollment { get; set; }

        /// <summary>
        /// whether or not user registration needs admin's manual approval
        /// </summary>
        [JsonProperty("auto_approve")]
        public bool AutoApprove { get; set; }

        /// <summary>
        /// tags. An array of any string. At most 20 tags.
        /// </summary>
        [MaxLength(20)]
        [JsonProperty("tags")]
        public string[] Tags { get; set; }

        /// <summary>
        /// The timestamp when the hackathon is created
        /// </summary>
        [JsonProperty("created_at")]
        public DateTime CreatedTime { get; set; }

        /// <summary>
        /// The timestamp when the hackathon starts.
        /// </summary>
        [JsonProperty("event_started_at")]
        public DateTime EventStartTime { get; set; }

        /// <summary>
        /// The timestamp when the hackathon ends
        /// </summary>
        [JsonProperty("event_ended_at")]
        public DateTime EventEndTime { get; set; }

        /// <summary>
        /// The timestamp when the hackathon begins to accept user enrollement
        /// </summary>
        [JsonProperty("enrollment_started_at")]
        public DateTime EnrollmentStartTime { get; set; }

        /// <summary>
        /// The timestamp when the hackathon stops accepting user enrollement
        /// </summary>
        [JsonProperty("enrollment_ended_at")]
        public DateTime EnrollmentEndTime { get; set; }

        /// <summary>
        /// The timestamp when the judges begin to review and rate the output showed/uploaded by enrolled users
        /// </summary>
        [JsonProperty("judge_started_at")] public DateTime JudgeStartTime { get; set; }

        /// <summary>
        /// The timestamp when the reviews/ratings should be completed.
        /// </summary>
        [JsonProperty("judge_ended_at")] public DateTime JudgeEndTime { get; set; }
    }
}
