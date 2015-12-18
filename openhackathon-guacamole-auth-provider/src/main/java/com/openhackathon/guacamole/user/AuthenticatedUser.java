/*
 * Copyright (C) 2015 Glyptodon LLC
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */
package com.openhackathon.guacamole.user;

import com.google.inject.Inject;
import org.glyptodon.guacamole.net.auth.AbstractAuthenticatedUser;
import org.glyptodon.guacamole.net.auth.AuthenticationProvider;
import org.glyptodon.guacamole.net.auth.Connection;
import org.glyptodon.guacamole.net.auth.Credentials;

import java.util.Map;

/**
 * An openhackthon-specific implementation of AuthenticatedUser, associating a
 * particular set of credentials with the openhackthon authentication provider.
 */
public class AuthenticatedUser extends AbstractAuthenticatedUser {

    /**
     * Reference to the authentication provider associated with this
     * authenticated user.
     */
    @Inject
    private AuthenticationProvider authProvider;

    /**
     * The credentials provided when this user was authenticated.
     */
    private Credentials credentials;

    /**
     * All connections to which this user has access.
     */
    private Map<String, Connection> connections;

    /**
     * Initializes this AuthenticatedUser using the given credentials and map
     * of connections.
     *
     * @param credentials
     *     The credentials provided when this user was authenticated.
     *
     * @param connections
     *     The connections that this user should have access to.
     */
    public void init(Credentials credentials, Map<String, Connection> connections) {
        this.credentials = credentials;
        this.connections = connections;
        setIdentifier(credentials.getUsername());
    }

    @Override
    public AuthenticationProvider getAuthenticationProvider() {
        return authProvider;
    }

    @Override
    public Credentials getCredentials() {
        return credentials;
    }

    /**
     * Returns a map containing all connections to which this user has access.
     * Each connection is stored within the map under its identifier.
     *
     * @return
     *     A map of all connections to which this user has access.
     */
    public Map<String, Connection> getConnections() {
        return connections;
    }
}
