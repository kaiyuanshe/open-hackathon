﻿using Kaiyuanshe.OpenHackathon.Server.Models.Validations;
using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;

namespace Kaiyuanshe.OpenHackathon.Server.Models
{
    /// <summary>
    /// Template to setup virtual experiment on Kubernetes. Not required.
    /// </summary>
    [RemoteConfigPolicy]
    public class Template : KubernetesModelBase
    {
        /// <summary>
        /// name of hackathon
        /// </summary>
        /// <example>foo</example>
        public string hackathonName { get; internal set; }

        /// <summary>
        /// name of template. Auto-generated by hackathon server.
        /// </summary>
        /// <example>default</example>
        public string name { get; internal set; }

        /// <summary>
        /// display name.
        /// </summary>
        /// <example>Ubuntu 20.04 LTS</example>
        public string displayName { get; set; }

        /// <summary>
        /// Container image.
        /// </summary>
        /// <example>jenkins/jenkins:lts</example>
        [MaxLength(128)]
        [Required]
        public string image { get; set; }

        /// <summary>
        /// commands to start a container.
        /// </summary>
        /// <example>[ "bash", "-c", "vncserver :1 -localhost no -geometry 1920*1080 -depth 24" ]</example>
        [Required]
        [MinLength(1)]
        public string[] commands { get; set; }

        /// <summary>
        /// environment variables passed to the container.
        /// </summary>
        /// <example>{ "FOO": "bar", "KEY": "value" }</example>
        [EnvironmentVariables]
        public Dictionary<string, string> environmentVariables { get; set; }
        
        /// <summary>
        /// protocol for remote connection
        /// </summary>
        /// <example>vnc</example>
        [Required]
        public IngressProtocol ingressProtocol { get; set; }

        /// <summary>
        /// Port exposed by the container image. Note this is not the actual port for remote connection.
        /// The actual port is auto-generated during runtime and is invisible to external.
        /// </summary>
        /// <example>5901</example>
        [Required]
        [Range(1, 65535)]
        public int ingressPort { get; set; }

        /// <summary>
        /// vnc settings. Required ingressProtocol is vnc.
        /// </summary>
        public Vnc vnc { get; set; }
    }

    /// <summary>
    /// vnc configurations.
    /// </summary>
    public class Vnc
    {
        /// <summary>
        /// login user name for remote connection. lowercase chars and numbers only: ^[a-z][a-z0-9]{1,63}$
        /// </summary>
        /// <example>johndoe</example>
        [RegularExpression("^[a-z][a-z0-9]{1,63}$")]
        public string userName { get; set; }

        /// <summary>
        /// login password for remote connection. 
        /// </summary>
        /// <example>mypassword</example>
        [MinLength(6)]
        [MaxLength(64)]
        public string password { get; set; }
    }

    /// <summary>
    /// protocol for remote connection.
    /// </summary>
    public enum IngressProtocol
    {
        ssh,
        vnc,
        rdp,
    }
}