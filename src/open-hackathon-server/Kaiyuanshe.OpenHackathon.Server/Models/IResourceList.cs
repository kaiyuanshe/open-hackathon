namespace Kaiyuanshe.OpenHackathon.Server.Models
{
    /// <summary>
    /// decribes a resource list
    /// </summary>
    public interface IResourceList<T>
    {
        /// <summary>
        /// List of the resources
        /// </summary>
        T[] value { get; set; }

        /// <summary>
        /// The URL the client should use to fetch the next page (per server side paging).
        /// No more results if it's null or empty.
        /// </summary>
        /// <example>https://hackathon-api.kaiyuanshe.cn/...pathToMoreResults...</example>
        string nextLink { get; set; }
    }

    public abstract class ResourceList<T> : IResourceList<T>
    {
        public abstract T[] value { get; set; }

        /// <summary>
        /// The URL the client should use to fetch the next page (per server side paging).
        /// No more results if it's null or empty.
        /// </summary>
        /// <example>https://hackathon-api.kaiyuanshe.cn/...pathToMoreResults...</example>
        public string nextLink { get; set; }
    }
}
