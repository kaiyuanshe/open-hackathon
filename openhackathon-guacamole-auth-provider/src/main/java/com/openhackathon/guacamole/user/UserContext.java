/*
 * Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
 *
 * The MIT License (MIT)
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
import com.openhackathon.guacamole.OpenHackathonAuthenticationProvider;
import org.glyptodon.guacamole.GuacamoleException;
import org.glyptodon.guacamole.form.Form;
import org.glyptodon.guacamole.net.auth.*;
import org.glyptodon.guacamole.net.auth.AuthenticatedUser;
import org.glyptodon.guacamole.net.auth.simple.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Collection;
import java.util.Collections;
import java.util.Map;

/**
 * An openhackthon-specific implementation of UserContex which queries all Guacamole
 * connections from openhackthon server.
 */
public class UserContext implements org.glyptodon.guacamole.net.auth.UserContext {

    /**
     * Logger for this class.
     */
    private final Logger logger = LoggerFactory.getLogger(UserContext.class);

    /**
     * Reference to the AuthenticationProvider associated with this
     * UserContext.
     */
    @Inject
    private AuthenticationProvider authProvider;

    /**
     * Reference to a User object representing the user whose access level
     * dictates the users and connections visible through this UserContext.
     */
    private User self;

    /**
     * Directory containing all User objects accessible to the user associated
     * with this UserContext.
     */
    private Directory<User> userDirectory;

    /**
     * Directory containing all Connection objects accessible to the user
     * associated with this UserContext.
     */
    private Directory<Connection> connectionDirectory;

    /**
     * Directory containing all ConnectionGroup objects accessible to the user
     * associated with this UserContext.
     */
    private Directory<ConnectionGroup> connectionGroupDirectory;

    /**
     * Reference to the root connection group.
     */
    private ConnectionGroup rootGroup;


    /**
     * Initializes this UserContext using the provided AuthenticatedUser and
     * Map of Connections.
     *
     * @param user
     *     The AuthenticatedUser representing the user that authenticated. This
     *     user may have been authenticated by a different authentication
     *     provider.
     *
     * @param connections
     *     The Map of Connections that this UserContext should provide access
     *     to.
     */
    public void init(AuthenticatedUser user,
                     Map<String, Connection> connections) {
        //There may be some problem here.
        // Init self with basic permissions
        self = new SimpleUser(
                user.getIdentifier(),
                Collections.singleton(user.getIdentifier()),
                connections.keySet(),
                Collections.singleton(OpenHackathonAuthenticationProvider.ROOT_CONNECTION_GROUP)
        );

        // Add all accessible connections
        connectionDirectory = new SimpleDirectory<Connection>(connections);

        // Root group contains only the provided connections
        rootGroup = new SimpleConnectionGroup(
                OpenHackathonAuthenticationProvider.ROOT_CONNECTION_GROUP,
                OpenHackathonAuthenticationProvider.ROOT_CONNECTION_GROUP,
                connections.keySet(),
                Collections.<String>emptyList()
        );

        // Expose only the root group in the connection group directory
        connectionGroupDirectory = new SimpleConnectionGroupDirectory(Collections.singleton(rootGroup));

        // The user directory contains only the current user
        userDirectory = new SimpleUserDirectory(self);
    }

    @Override
    public User self() {
        return self;
    }

    @Override
    public AuthenticationProvider getAuthenticationProvider() {
        return authProvider;
    }

    @Override
    public Directory<User> getUserDirectory() throws GuacamoleException {
        return userDirectory;
    }

    @Override
    public Directory<Connection> getConnectionDirectory() throws GuacamoleException {
        return connectionDirectory;
    }

    @Override
    public Directory<ConnectionGroup> getConnectionGroupDirectory() throws GuacamoleException {
        return connectionGroupDirectory;
    }

    @Override
    public Directory<ActiveConnection> getActiveConnectionDirectory() throws GuacamoleException {
        return new SimpleDirectory<ActiveConnection>();
    }

    @Override
    public ConnectionRecordSet getConnectionHistory() throws GuacamoleException {
        return new SimpleConnectionRecordSet();
    }

    @Override
    public ConnectionGroup getRootConnectionGroup() throws GuacamoleException {
        return rootGroup;
    }

    @Override
    public Collection<Form> getUserAttributes() {
        return Collections.<Form>emptyList();
    }

    @Override
    public Collection<Form> getConnectionAttributes() {
        return Collections.<Form>emptyList();
    }

    @Override
    public Collection<Form> getConnectionGroupAttributes() {
        return Collections.<Form>emptyList();
    }
}
