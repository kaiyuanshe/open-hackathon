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
package com.openhackathon.guacamole;

import com.google.inject.Inject;
import com.google.inject.Provider;
import com.openhackathon.guacamole.connection.ConnectionService;
import com.openhackathon.guacamole.user.AuthenticatedUser;
import org.glyptodon.guacamole.GuacamoleException;
import org.glyptodon.guacamole.net.auth.Connection;
import org.glyptodon.guacamole.net.auth.Credentials;
import org.glyptodon.guacamole.net.auth.UserContext;
import org.glyptodon.guacamole.net.auth.credentials.CredentialsInfo;
import org.glyptodon.guacamole.net.auth.credentials.GuacamoleInvalidCredentialsException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Map;

/**
 * Service providing convenience functions for the LDAP AuthenticationProvider
 * implementation.
 */
public class AuthenticationProviderService {
    /**
     * Logger for this class.
     */
    private final Logger logger = LoggerFactory.getLogger(AuthenticationProviderService.class);

    /**
     * Provider for AuthenticatedUser objects.
     */
    @Inject
    private Provider<AuthenticatedUser> authenticatedUserProvider;

    /**
     * Service which provides connections to open hackthon instances.
     */
    @Inject
    private ConnectionService connectionService;

    /**
     * Provider for UserContext objects.
     */
    @Inject
    private Provider<UserContext> userContextProvider;

    /**
     * Returns an AuthenticatedUser representing the user authenticated by the
     * given credentials.
     *
     * @param credentials
     *     The credentials to use for authentication.
     *
     * @return
     *     An AuthenticatedUser representing the user authenticated by the
     *     given credentials.
     *
     * @throws GuacamoleException
     *     If an error occurs while authenticating the user, or if access is
     *     denied.
     */
    public AuthenticatedUser authenticateUser(Credentials credentials)
            throws GuacamoleException {

        //Validate login
        Map<String, Connection> connections = connectionService.getConnections(credentials);
        if (connections == null) {
            throw new GuacamoleInvalidCredentialsException("Invalid login.",
                    CredentialsInfo.USERNAME_PASSWORD);
        }

        // Return AuthenticatedUser if login succeeds, caching retrieved connections
        AuthenticatedUser authenticatedUser = authenticatedUserProvider.get();
        authenticatedUser.init(credentials, connections);
        return authenticatedUser;
    }


    /**
     * Returns a UserContext object initialized with data accessible to the
     * given AuthenticatedUser.
     *
     * @param authenticatedUser
     *     The AuthenticatedUser to retrieve data for.
     *
     * @return
     *     A UserContext object initialized with data accessible to the given
     *     AuthenticatedUser.
     *
     * @throws GuacamoleException
     *     If the UserContext cannot be created due to an error.
     */
    public UserContext getUserContext(org.glyptodon.guacamole.net.auth.AuthenticatedUser authenticatedUser)
            throws GuacamoleException {

        return null;
    }

}
