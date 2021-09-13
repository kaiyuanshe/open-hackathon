namespace Kaiyuanshe.OpenHackathon.Server.Models
{
    /// <summary>
    /// Describes a running system on cloud.
    /// </summary>
    public class Experiment : KubernetesModelBase
    {
        /// <summary>
        /// name of hackathon
        /// </summary>
        /// <example>foo</example>
        public string hackathonName { get; internal set; }

        /// <summary>
        /// auto-generated id of the experiment.
        /// </summary>
        /// <example>6129c741-87e5-4a78-8173-f80724a70aea</example>
        public string id { get; internal set; }

        /// <summary>
        /// name of template. Retained for future use. Input is ignored for now.
        /// </summary>
        /// <example>default</example>
        public string templateName { get; set; }

        /// <summary>
        /// id of user
        /// </summary>
        /// <example>1</example>
        public string userId { get; internal set; }

        /// <summary>
        /// Detailed user info of the member
        /// </summary>
        public UserInfo user { get; internal set; }
    }
}
