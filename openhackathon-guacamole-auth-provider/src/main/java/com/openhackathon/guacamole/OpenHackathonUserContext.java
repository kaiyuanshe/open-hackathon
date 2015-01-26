package com.openhackathon.guacamole;



import java.util.Collections;
import java.util.Map;

import org.glyptodon.guacamole.GuacamoleException;
import org.glyptodon.guacamole.net.auth.ConnectionGroup;
import org.glyptodon.guacamole.net.auth.Directory;
import org.glyptodon.guacamole.net.auth.User;
import org.glyptodon.guacamole.net.auth.UserContext;
import org.glyptodon.guacamole.net.auth.simple.SimpleConnectionGroup;
import org.glyptodon.guacamole.net.auth.simple.SimpleConnectionGroupDirectory;
import org.glyptodon.guacamole.net.auth.simple.SimpleUser;
import org.glyptodon.guacamole.net.auth.simple.SimpleUserContext;
import org.glyptodon.guacamole.net.auth.simple.SimpleUserDirectory;
import org.glyptodon.guacamole.protocol.GuacamoleConfiguration;

/**
 * An extremely simple UserContext implementation which provides access to
 * a defined and restricted set of GuacamoleConfigurations. Access to
 * querying or modifying either users or permissions is denied.
 *
 * @author Michael Jumper
 */
public class OpenHackathonUserContext implements UserContext {


    private User self;
    private Directory<String, User> userDirectory;
    private ConnectionGroup connectionGroup;


    public OpenHackathonUserContext(Map<String, GuacamoleConfiguration> configs) {

        // Add root group that contains only configurations
        this.connectionGroup = new SimpleConnectionGroup("ROOT", "ROOT",
                new OpenHackathonConnectionDirectory(configs),
                new SimpleConnectionGroupDirectory(Collections.EMPTY_LIST));

        // Build new user from credentials, giving the user an arbitrary name
        this.self = new SimpleUser("user",
                configs, Collections.singleton(connectionGroup));

        // Create user directory for new user
        this.userDirectory = new SimpleUserDirectory(self);
        
    }

    @Override
    public User self() {
        return self;
    }

    @Override
    public Directory<String, User> getUserDirectory()
            throws GuacamoleException {
        return userDirectory;
    }

    @Override
    public ConnectionGroup getRootConnectionGroup() throws GuacamoleException {
        return connectionGroup;
    }

}
