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
package com.openhackathon.guacamole;


import com.google.inject.Guice;
import com.google.inject.Injector;
import org.glyptodon.guacamole.GuacamoleException;
import org.glyptodon.guacamole.net.auth.AuthenticatedUser;
import org.glyptodon.guacamole.net.auth.AuthenticationProvider;
import org.glyptodon.guacamole.net.auth.Credentials;
import org.glyptodon.guacamole.net.auth.UserContext;

public class OpenHackathonAuthenticationProvider implements AuthenticationProvider {
    /**
     * The identifier reserved for the root connection group.
     */
    public static final String ROOT_CONNECTION_GROUP = "ROOT";

    /**
     * Injector which will manage the object graph of this authentication
     * provider.
     */
    private final Injector injector;

    /**
     * Creates a new AWSAuthenticationProvider that pulls user connection data
     * from AWS.
     *
     * @throws GuacamoleException
     *     If a required property is missing, or an error occurs while parsing
     *     a property.
     */
    public OpenHackathonAuthenticationProvider() throws GuacamoleException {

        // Set up Guice injector.
        injector = Guice.createInjector(
                new OpenHackthonAuthenticationProviderModule(this)
        );
    }


    @Override
    public String getIdentifier() {
        return "openhackthon";
    }

    @Override
    public AuthenticatedUser authenticateUser(Credentials credentials) throws GuacamoleException {
        //TODO credentials may be updated???
        AuthenticationProviderService authProviderService = injector.getInstance(AuthenticationProviderService.class);
        return authProviderService.authenticateUser(credentials);
    }

    @Override
    public AuthenticatedUser updateAuthenticatedUser(AuthenticatedUser authenticatedUser, Credentials credentials) throws GuacamoleException {
        //TODO credentials may be updated???
        return authenticatedUser;
    }

    @Override
    public UserContext getUserContext(AuthenticatedUser authenticatedUser) throws GuacamoleException {
        //TODO credentials may be updated???
        AuthenticationProviderService authProviderService = injector.getInstance(AuthenticationProviderService.class);
        return authProviderService.getUserContext(authenticatedUser);
    }

    @Override
    public UserContext updateUserContext(UserContext context, AuthenticatedUser authenticatedUser) throws GuacamoleException {
        //TODO credentials may be updated???
        return context;
    }
}
