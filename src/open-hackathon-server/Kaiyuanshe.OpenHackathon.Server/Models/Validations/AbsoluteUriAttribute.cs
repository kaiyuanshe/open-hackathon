using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Models.Validations
{
    [AttributeUsage(AttributeTargets.Property)]
    public class AbsoluteUriAttribute : ValidationAttribute
    {
        protected override ValidationResult IsValid(object value, ValidationContext validationContext)
        {
            if (value == null)
            {
                // leave it to Required
                return ValidationResult.Success;
            }

            string uri = value.ToString();
            if (Uri.TryCreate(uri, UriKind.Absolute, out Uri temp))
            {
                if(temp.Scheme.ToUpper() != "HTTPS" && temp.Scheme.ToUpper() != "HTTP")
                {
                    return new ValidationResult($"invalid Uri: {uri}");
                }

                return ValidationResult.Success;
            }
            else
            {
                return new ValidationResult($"invalid Uri: {uri}");
            }
        }
    }
}
