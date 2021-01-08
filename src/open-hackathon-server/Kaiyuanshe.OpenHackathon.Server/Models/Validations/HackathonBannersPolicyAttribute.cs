using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Models.Validations
{
    [AttributeUsage(AttributeTargets.Property)]
    public class HackathonBannersPolicyAttribute : ValidationAttribute
    {
        static readonly int MaxBannerCount = 10;

        protected override ValidationResult IsValid(object value, ValidationContext validationContext)
        {
            if (value == null)
            {
                // leave it to RequiredAttribute
                return ValidationResult.Success;
            }

            string[] banners = (string[])value;
            if (banners.Length == 0)
            {
                return new ValidationResult("Need at least 1 banner image.");
            }
            if (banners.Length > MaxBannerCount)
            {
                return new ValidationResult($"A maximum of {MaxBannerCount} banners are supported. Banners in request is {banners.Length}");
            }

            Uri temp;
            var invalidUris = banners.Where(b => !Uri.TryCreate(b, UriKind.Absolute, out temp));
            if (invalidUris.Count() > 0)
            {
                return new ValidationResult("Invalid banner Uri", invalidUris);
            }

            return ValidationResult.Success;
        }
    }
}
