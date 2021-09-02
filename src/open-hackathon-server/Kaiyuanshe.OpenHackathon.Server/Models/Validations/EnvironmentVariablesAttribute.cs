using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Models.Validations
{
    [AttributeUsage(AttributeTargets.Property)]
    public class EnvironmentVariablesAttribute : ValidationAttribute
    {
        private static readonly int NameMaxLength = 64;
        private static readonly int ValueMaxLength = 256;
        private static readonly int MaxEnvs = 32;

        protected override ValidationResult IsValid(object value, ValidationContext validationContext)
        {
            if (value == null)
            {
                // leave it to Required
                return ValidationResult.Success;
            }

            Dictionary<string, string> envs = value as Dictionary<string, string>;
            if (envs.Count > MaxEnvs)
            {
                return new ValidationResult($"a maximum of {MaxEnvs} environment variables are allowed.");
            }

            List<string> invalidMembers = new List<string>();
            invalidMembers.AddRange(envs.Keys.Where(k => k.Length > NameMaxLength));
            invalidMembers.AddRange(envs.Values.Where(k => k.Length > ValueMaxLength));
            if (invalidMembers.Count > 0)
            {
                string msg = $"For every env variable, the name must not exeed {NameMaxLength} in length, and the value must not exceed {ValueMaxLength} in length.";
                return new ValidationResult(msg, invalidMembers);
            }

            return ValidationResult.Success;
        }
    }
}
