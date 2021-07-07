﻿//------------------------------------------------------------------------------
// <auto-generated>
//     This code was generated by a tool.
//     Runtime Version:4.0.30319.42000
//
//     Changes to this file may cause incorrect behavior and will be lost if
//     the code is regenerated.
// </auto-generated>
//------------------------------------------------------------------------------

namespace Kaiyuanshe.OpenHackathon.Server {
    using System;
    
    
    /// <summary>
    ///   A strongly-typed resource class, for looking up localized strings, etc.
    /// </summary>
    // This class was auto-generated by the StronglyTypedResourceBuilder
    // class via a tool like ResGen or Visual Studio.
    // To add or remove a member, edit your .ResX file then rerun ResGen
    // with the /str option, or rebuild your VS project.
    [global::System.CodeDom.Compiler.GeneratedCodeAttribute("System.Resources.Tools.StronglyTypedResourceBuilder", "16.0.0.0")]
    [global::System.Diagnostics.DebuggerNonUserCodeAttribute()]
    [global::System.Runtime.CompilerServices.CompilerGeneratedAttribute()]
    internal class Resources {
        
        private static global::System.Resources.ResourceManager resourceMan;
        
        private static global::System.Globalization.CultureInfo resourceCulture;
        
        [global::System.Diagnostics.CodeAnalysis.SuppressMessageAttribute("Microsoft.Performance", "CA1811:AvoidUncalledPrivateCode")]
        internal Resources() {
        }
        
        /// <summary>
        ///   Returns the cached ResourceManager instance used by this class.
        /// </summary>
        [global::System.ComponentModel.EditorBrowsableAttribute(global::System.ComponentModel.EditorBrowsableState.Advanced)]
        internal static global::System.Resources.ResourceManager ResourceManager {
            get {
                if (object.ReferenceEquals(resourceMan, null)) {
                    global::System.Resources.ResourceManager temp = new global::System.Resources.ResourceManager("Kaiyuanshe.OpenHackathon.Server.Resources", typeof(Resources).Assembly);
                    resourceMan = temp;
                }
                return resourceMan;
            }
        }
        
        /// <summary>
        ///   Overrides the current thread's CurrentUICulture property for all
        ///   resource lookups using this strongly typed resource class.
        /// </summary>
        [global::System.ComponentModel.EditorBrowsableAttribute(global::System.ComponentModel.EditorBrowsableState.Advanced)]
        internal static global::System.Globalization.CultureInfo Culture {
            get {
                return resourceCulture;
            }
            set {
                resourceCulture = value;
            }
        }
        
        /// <summary>
        ///   Looks up a localized string similar to Forbidden. The user associated with the token doesn&apos;t have proper permission. Please contact the administrator for access..
        /// </summary>
        internal static string Auth_Forbidden {
            get {
                return ResourceManager.GetString("Auth_Forbidden", resourceCulture);
            }
        }
        
        /// <summary>
        ///   Looks up a localized string similar to The access token cannot be validated. Code:{0}, Message:{1}.
        /// </summary>
        internal static string Auth_Token_ValidateRemoteFailed {
            get {
                return ResourceManager.GetString("Auth_Token_ValidateRemoteFailed", resourceCulture);
            }
        }
        
        /// <summary>
        ///   Looks up a localized string similar to Token expired at {0}. Please re-login..
        /// </summary>
        internal static string Auth_TokenExpired {
            get {
                return ResourceManager.GetString("Auth_TokenExpired", resourceCulture);
            }
        }
        
        /// <summary>
        ///   Looks up a localized string similar to Token is either missing or invalid. Please add it to Http request headers: Headers[&quot;Authorization&quot;]=token TOKEN. .
        /// </summary>
        internal static string Auth_Unauthorized {
            get {
                return ResourceManager.GetString("Auth_Unauthorized", resourceCulture);
            }
        }
        
        /// <summary>
        ///   Looks up a localized string similar to The award is assigned hence cannot delete. Please delete the assignments first..
        /// </summary>
        internal static string Award_CannotDeleteAssigned {
            get {
                return ResourceManager.GetString("Award_CannotDeleteAssigned", resourceCulture);
            }
        }
        
        /// <summary>
        ///   Looks up a localized string similar to `award.target` cannot be updated since the award is already assigned to a team or user. Please delete the assignment(s) first..
        /// </summary>
        internal static string Award_CannotUpdateTarget {
            get {
                return ResourceManager.GetString("Award_CannotUpdateTarget", resourceCulture);
            }
        }
        
        /// <summary>
        ///   Looks up a localized string similar to Award with specified id is not found..
        /// </summary>
        internal static string Award_NotFound {
            get {
                return ResourceManager.GetString("Award_NotFound", resourceCulture);
            }
        }
        
        /// <summary>
        ///   Looks up a localized string similar to Cannot assign the award to more than {0} assignees..
        /// </summary>
        internal static string Award_TooManyAssignments {
            get {
                return ResourceManager.GetString("Award_TooManyAssignments", resourceCulture);
            }
        }
        
        /// <summary>
        ///   Looks up a localized string similar to The assignment is not found..
        /// </summary>
        internal static string AwardAssignment_NotFound {
            get {
                return ResourceManager.GetString("AwardAssignment_NotFound", resourceCulture);
            }
        }
        
        /// <summary>
        ///   Looks up a localized string similar to Enrollment already ended at {0}.
        /// </summary>
        internal static string Enrollment_Ended {
            get {
                return ResourceManager.GetString("Enrollment_Ended", resourceCulture);
            }
        }
        
        /// <summary>
        ///   Looks up a localized string similar to Enrollment cannot be fullfilled since it has reached the quota..
        /// </summary>
        internal static string Enrollment_Full {
            get {
                return ResourceManager.GetString("Enrollment_Full", resourceCulture);
            }
        }
        
        /// <summary>
        ///   Looks up a localized string similar to Enrollment not approved yet. Please contact the hackathon admistrators for approval..
        /// </summary>
        internal static string Enrollment_NotApproved {
            get {
                return ResourceManager.GetString("Enrollment_NotApproved", resourceCulture);
            }
        }
        
        /// <summary>
        ///   Looks up a localized string similar to User {0} not enrolled in hackathon {1}.
        /// </summary>
        internal static string Enrollment_NotFound {
            get {
                return ResourceManager.GetString("Enrollment_NotFound", resourceCulture);
            }
        }
        
        /// <summary>
        ///   Looks up a localized string similar to Enrollment not started. The enrollment will be accepted starting from {0}.
        /// </summary>
        internal static string Enrollment_NotStarted {
            get {
                return ResourceManager.GetString("Enrollment_NotStarted", resourceCulture);
            }
        }
        
        /// <summary>
        ///   Looks up a localized string similar to Count of extensions exceeds the allowed limit {0}..
        /// </summary>
        internal static string Enrollment_TooManyExtensions {
            get {
                return ResourceManager.GetString("Enrollment_TooManyExtensions", resourceCulture);
            }
        }
        
        /// <summary>
        ///   Looks up a localized string similar to Hackathon {0} is already Online..
        /// </summary>
        internal static string Hackathon_AlreadyOnline {
            get {
                return ResourceManager.GetString("Hackathon_AlreadyOnline", resourceCulture);
            }
        }
        
        /// <summary>
        ///   Looks up a localized string similar to Hackathon {0} is Offline. Cannot be updated..
        /// </summary>
        internal static string Hackathon_Deleted {
            get {
                return ResourceManager.GetString("Hackathon_Deleted", resourceCulture);
            }
        }
        
        /// <summary>
        ///   Looks up a localized string similar to The hackathon is already ended at {0}.
        /// </summary>
        internal static string Hackathon_Ended {
            get {
                return ResourceManager.GetString("Hackathon_Ended", resourceCulture);
            }
        }
        
        /// <summary>
        ///   Looks up a localized string similar to The name is invalid. Must contain only letters and/or numbers, length between 1 and 100..
        /// </summary>
        internal static string Hackathon_Name_Invalid {
            get {
                return ResourceManager.GetString("Hackathon_Name_Invalid", resourceCulture);
            }
        }
        
        /// <summary>
        ///   Looks up a localized string similar to The name is already used. Please try another name..
        /// </summary>
        internal static string Hackathon_Name_Taken {
            get {
                return ResourceManager.GetString("Hackathon_Name_Taken", resourceCulture);
            }
        }
        
        /// <summary>
        ///   Looks up a localized string similar to Access denied. Only the admins of the hackathon are allowed. Please contact the admin to request access..
        /// </summary>
        internal static string Hackathon_NotAdmin {
            get {
                return ResourceManager.GetString("Hackathon_NotAdmin", resourceCulture);
            }
        }
        
        /// <summary>
        ///   Looks up a localized string similar to Hackathon with name `{0}` not found. Try PUT to create a new one..
        /// </summary>
        internal static string Hackathon_NotFound {
            get {
                return ResourceManager.GetString("Hackathon_NotFound", resourceCulture);
            }
        }
        
        /// <summary>
        ///   Looks up a localized string similar to The hackathon is not started yet. .
        /// </summary>
        internal static string Hackathon_NotStarted {
            get {
                return ResourceManager.GetString("Hackathon_NotStarted", resourceCulture);
            }
        }
        
        /// <summary>
        ///   Looks up a localized string similar to Hackathon is archived and is ReadOnly..
        /// </summary>
        internal static string Hackathon_ReadOnly {
            get {
                return ResourceManager.GetString("Hackathon_ReadOnly", resourceCulture);
            }
        }
        
        /// <summary>
        ///   Looks up a localized string similar to An unexpected exception occurs. Please try again later or report an issue at https://github.com/kaiyuanshe/open-hackathon/issues.
        /// </summary>
        internal static string Hackathon_UnhandledException {
            get {
                return ResourceManager.GetString("Hackathon_UnhandledException", resourceCulture);
            }
        }
        
        /// <summary>
        ///   Looks up a localized string similar to Required parameter {0} is null or empty..
        /// </summary>
        internal static string Parameter_Required {
            get {
                return ResourceManager.GetString("Parameter_Required", resourceCulture);
            }
        }
        
        /// <summary>
        ///   Looks up a localized string similar to Cannot delete the team for awards are assigned to this team. Please delete the award assignments first..
        /// </summary>
        internal static string Team_HasAward {
            get {
                return ResourceManager.GetString("Team_HasAward", resourceCulture);
            }
        }
        
        /// <summary>
        ///   Looks up a localized string similar to Access denied. Please contact admins of the team..
        /// </summary>
        internal static string Team_NotAdmin {
            get {
                return ResourceManager.GetString("Team_NotAdmin", resourceCulture);
            }
        }
        
        /// <summary>
        ///   Looks up a localized string similar to Cannot create a new team. must enroll first..
        /// </summary>
        internal static string Team_NotEnrolled {
            get {
                return ResourceManager.GetString("Team_NotEnrolled", resourceCulture);
            }
        }
        
        /// <summary>
        ///   Looks up a localized string similar to Team with specified id is not found..
        /// </summary>
        internal static string Team_NotFound {
            get {
                return ResourceManager.GetString("Team_NotFound", resourceCulture);
            }
        }
        
        /// <summary>
        ///   Looks up a localized string similar to Member {0} is not allowed to perform this operation..
        /// </summary>
        internal static string TeamMember_AccessDenied {
            get {
                return ResourceManager.GetString("TeamMember_AccessDenied", resourceCulture);
            }
        }
        
        /// <summary>
        ///   Looks up a localized string similar to The user cannot be removed since there are more than 1 members and the user is the only admin with admin access..
        /// </summary>
        internal static string TeamMember_LastAdmin {
            get {
                return ResourceManager.GetString("TeamMember_LastAdmin", resourceCulture);
            }
        }
        
        /// <summary>
        ///   Looks up a localized string similar to Member {0} is not a member of team {1}.
        /// </summary>
        internal static string TeamMember_NotFound {
            get {
                return ResourceManager.GetString("TeamMember_NotFound", resourceCulture);
            }
        }
        
        /// <summary>
        ///   Looks up a localized string similar to The specified user is not found..
        /// </summary>
        internal static string User_NotFound {
            get {
                return ResourceManager.GetString("User_NotFound", resourceCulture);
            }
        }
    }
}
