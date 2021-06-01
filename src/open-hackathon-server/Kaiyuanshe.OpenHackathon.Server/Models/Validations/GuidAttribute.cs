using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Models.Validations
{
    [AttributeUsage(AttributeTargets.Property)]
    public class GuidAttribute : ValidationAttribute
    {
        protected override ValidationResult IsValid(object value, ValidationContext validationContext)
        {
            if (value == null)
            {
                // leave it to Required
                return ValidationResult.Success;
            }

            if (Guid.TryParse(value.ToString(), out Guid guid))
            {
                return ValidationResult.Success;
            }
            else
            {
                return new ValidationResult($"`{value.ToString()}` is not a valid GUID.");
            }
        }
    }
}
