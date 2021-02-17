using System;
using System.Security.Cryptography;
using System.Text;

namespace Kaiyuanshe.OpenHackathon.Server
{
    public static class DigestHelper
    {
        [ThreadStatic] private static SHA512Managed _sha512;

        private static SHA512Managed SHA512 => _sha512 ?? (_sha512 = new SHA512Managed());

        public static string SHA512Digest(byte[] bytes)
        {
            byte[] hash = SHA512.ComputeHash(bytes);
            return toHexString(hash);
        }

        public static string SHA512Digest(string content)
        {
            return SHA512Digest(Encoding.UTF8.GetBytes(content));
        }

        private static string toHexString(byte[] bytes)
        {
            if (bytes == null)
            {
                return null;
            }
            StringBuilder sb = new StringBuilder(bytes.Length * 2);
            foreach (byte b in bytes)
            {
                sb.Append(b.ToString("x2"));
            }
            return sb.ToString();
        }
    }
}
