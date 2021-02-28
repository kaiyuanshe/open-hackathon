using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Middlewares
{
    public class LoggingMiddleware
    {
        private readonly RequestDelegate _next;
        private ILogger<LoggingMiddleware> logger;
        static readonly int MaxBlockSize = 10 * 1024;

        public LoggingMiddleware(RequestDelegate next, ILogger<LoggingMiddleware> logger)
        {
            _next = next;
            this.logger = logger;
        }

        public async Task Invoke(HttpContext context)
        {
            if (!context.Request.Path.StartsWithSegments("/v2", StringComparison.OrdinalIgnoreCase))
            {
                // only logging APIs
                await _next(context);
                return;
            }

            var start = Stopwatch.GetTimestamp();
            var responseStream = new HttpResponseStream(context.Response.Body);
            context.Response.Body = responseStream;

            // handle the request first.
            await _next(context);

            int elapsedMs = (int)GetElapsedMilliseconds(start, Stopwatch.GetTimestamp());
            var clientIp = context.Connection.RemoteIpAddress;
            var method = context.Request.Method;
            var path = context.Request.Path;
            var query = context.Request.QueryString;
            var statusCode = context.Response?.StatusCode;

            string requestBody = await RequestBody(context);
            string responseBody = responseStream.ToLogMessage();

            // 172.21.13.45 - GET "/scripts/iisadmin/ism.dll?http/serv" 200
            string message = $"[{elapsedMs}]{clientIp} - {method} '{path}{query}' {statusCode}";
            logger.TraceInformation(message);
            if (!string.IsNullOrEmpty(requestBody))
            {
                logger.TraceInformation(requestBody);
            }
            if (!string.IsNullOrWhiteSpace(responseBody))
            {
                logger.TraceInformation(responseBody);
            }
        }

        private static async Task<string> RequestBody(HttpContext context)
        {
            string requestBody = string.Empty;
            if (context.Request.Body.CanSeek)
            {
                try
                {
                    context.Request.Body.Seek(0, SeekOrigin.Begin);
                    using (StreamReader sr = new StreamReader(context.Request.Body))
                    {
                        long contentLength = context.Request.ContentLength.GetValueOrDefault();
                        int readBuffer = contentLength > MaxBlockSize ? MaxBlockSize : (int)contentLength;
                        char[] buffer = new char[readBuffer];
                        await sr.ReadAsync(buffer, 0, readBuffer);
                        requestBody = new string(buffer);
                    }
                }
                catch
                {
                    // ignore logging request
                }
            }

            return requestBody;
        }

        static double GetElapsedMilliseconds(long start, long stop)
        {
            return (stop - start) * 1000 / (double)Stopwatch.Frequency;
        }

        class HttpResponseStream : Stream
        {
            private Stream kestrel;
            private MemoryStream logStream = new MemoryStream();

            public HttpResponseStream(Stream kestrelResponseStream)
            {
                kestrel = kestrelResponseStream;
            }

            public override bool CanRead => kestrel.CanRead;

            public override bool CanSeek => kestrel.CanSeek;

            public override bool CanWrite => kestrel.CanWrite;

            public override long Length => kestrel.Length;

            public override long Position
            {
                get => kestrel.Position;
                set => kestrel.Position = value;
            }

            public override void Flush()
            {
                kestrel.Flush();
            }

            public override int Read(byte[] buffer, int offset, int count)
            {
                return kestrel.Read(buffer, offset, count);
            }

            public override long Seek(long offset, SeekOrigin origin)
            {
                return kestrel.Seek(offset, origin);
            }

            public override void SetLength(long value)
            {
                kestrel.SetLength(value);
            }

            public override Task WriteAsync(byte[] buffer, int offset, int count, CancellationToken cancellationToken)
            {
                if (logStream.Length < MaxBlockSize)
                {
                    logStream.Write(buffer, offset, Math.Min(count, MaxBlockSize - (int)logStream.Length));
                }
                return kestrel.WriteAsync(buffer, offset, count);
            }

            public override void Write(byte[] buffer, int offset, int count)
            {
                if (logStream.Length < MaxBlockSize)
                {
                    logStream.Write(buffer, offset, Math.Min(count, MaxBlockSize - (int)logStream.Length));
                }
            }

            internal string ToLogMessage()
            {
                logStream.Seek(0, SeekOrigin.Begin);
                using (StreamReader sr = new StreamReader(logStream))
                {
                    long contentLength = logStream.Length;
                    int readBuffer = contentLength > MaxBlockSize ? MaxBlockSize : (int)contentLength;
                    char[] buffer = new char[readBuffer];
                    sr.Read(buffer, 0, readBuffer);
                    return new string(buffer);
                }
            }
        }
    }
}
