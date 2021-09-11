using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Models
{
    public abstract class KubernetesModelBase : ModelBase
    {
        /// <summary>
        /// Status of the object in kubernetes
        /// </summary>
        /// <example>{"code": 200, "status": "success", "kind": "Status"}</example>
        public k8s.Models.V1Status status { get; internal set; }
    }
}
