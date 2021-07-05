using System;
using System.ComponentModel.DataAnnotations;

namespace Kaiyuanshe.OpenHackathon.Server.Models.Validations
{
    [AttributeUsage(AttributeTargets.Property | AttributeTargets.Parameter)]
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
