#!/bin/sh
#
# Copyright (C) 2013 Glyptodon LLC
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

#
# guacctl
# -------
#
# Utility for sending Guacamole-specific console codes for controlling the SSH
# session, such as:
#
#     * Downloading files
#     * Setting the destination directory for uploads
#
# This script may also be run as "guacget", in which case the script accepts
# no options and assumes anything given on the commandline is a file to be
# downloaded.
#


# Given the name of a file, which may be a relative path, produce the full,
# real, non-relative path for that same file.
fullpath() {
    FILENAME="$1"
    DIR=`dirname "$FILENAME"`
    FILE=`basename "$FILENAME"`
    (cd "$DIR" && echo "$PWD/$FILE")
}

# Sends the Guacamole-specific console code for initiating a download.
send_download_file() {
    FILENAME="$1"
    printf "\033]482200;%s\007" "$FILENAME"
}

# Sends the Guacamole-specific console code for setting the upload directory.
send_set_directory() {
    FILENAME="$1"
    printf "\033]482201;%s\007" "$FILENAME"
}

# Prints the given error text to STDERR.
error() {
    echo "$NAME:" "$@" >&2
}

# Prints usage documentation for this script.
usage() {
    cat >&2 <<END
guacctl 0.8.0, Guacamole SSH session control utility.
Usage: guacctl [OPTION] [FILE]...

    -d, --download         download each of the files listed.
    -s, --set-directory    set the destination directory for future uploaded 
                           files.
END
}

# Initiates a download for each of the specified files
download_files() {

    # Validate arguments
    if [ $# -lt 1 ]; then
        error "No files specified."
        return;
    fi

    for FILENAME in "$@"; do
        if [ -e "$FILENAME" ]; then
            send_download_file "`fullpath "$FILENAME"`"
        else
            error "$FILENAME: File does not exist."
        fi
    done

}

# Changes the upload path for future uploads to the given directory
set_directory() {

    # Validate arguments
    if [ $# -lt 1 ]; then
        error "No destination directory specified."
        return;
    fi

    if [ $# -gt 1 ]; then
        error "Only one destination directory may be given."
        return;
    fi

    FILENAME="$1"
    if [ -d "$FILENAME" ]; then
        send_set_directory "`fullpath "$FILENAME"`"
    else
        error "$FILENAME: File does not exist or is not a directory."
    fi

}

# Get script name
NAME=`basename "$0"`

# Parse options
if [ "x$NAME" = "xguacget" ]; then
    download_files "$@"
elif [ "x$1" = "x--download" -o "x$1" = "x-d" ]; then
    shift
    download_files "$@"
elif [ "x$1" = "x--set-directory" -o "x$1" = "x-s" ]; then
    shift
    set_directory "$@"
else
    usage
    exit 1
fi
