using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;

namespace Kaiyuanshe.OpenHackathon.Server.Models.Validations
{
    /// <summary>
    /// Add this Attribute if a property is Required for PUT(create) but optional for PATCH(update)
    /// </summary>
    [AttributeUsage(AttributeTargets.Property, AllowMultiple = false, Inherited = true)]
    public class RequiredIfPutAttribute : Attribute
    {

    }

    /// <summary>
    /// Check required parameters for PUT requests. 
    /// So we can re-use the same model while its properties can be Required for PUT but Optional for PATCH.
    /// </summary>
    [AttributeUsage(AttributeTargets.Parameter)]
    public class HttpPutPolicyAttribute : ValidationAttribute
    {
        protected override ValidationResult IsValid(object value, ValidationContext validationContext)
        {
            if (value == null)
            {
                // leave it to Required
                return ValidationResult.Success;
            }

            List<string> missingMembers = new List<string>();
            foreach (var property in value.GetType().GetProperties())
            {
                var attr = property.GetCustomAttributes(typeof(RequiredIfPutAttribute), true);
                if (attr.Any() && property.GetValue(value) == null)
                {
                    missingMembers.Add(property.Name);
                }
            }
            if (missingMembers.Count > 0)
            {
                return new ValidationResult("The member is required.", missingMembers);
            }

            return ValidationResult.Success;
        }
    }
}
