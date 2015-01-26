package com.openhackathon.guacamole;



import java.util.HashMap;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;

import org.glyptodon.guacamole.GuacamoleException;
import org.glyptodon.guacamole.GuacamoleSecurityException;
import org.glyptodon.guacamole.net.auth.Connection;
import org.glyptodon.guacamole.net.auth.Directory;
import org.glyptodon.guacamole.net.auth.simple.SimpleConnection;
import org.glyptodon.guacamole.protocol.GuacamoleConfiguration;


public class OpenHackathonConnectionDirectory implements Directory<String, Connection> {


    private Map<String, Connection> connections = new HashMap<String, Connection>();

    public OpenHackathonConnectionDirectory(Map<String, GuacamoleConfiguration> configs) {

        // Create connections for each config
        for (Entry<String, GuacamoleConfiguration> entry : configs.entrySet())
            connections.put(entry.getKey(),
            		new SimpleConnection(entry.getValue().getParameter("name"), entry.getValue().getProtocol(), entry.getValue()));
    }

    @Override
    public Connection get(String identifier)
            throws GuacamoleException {
        return connections.get(identifier);
    }

    @Override
    public Set<String> getIdentifiers() throws GuacamoleException {
        return connections.keySet();
    }

    @Override
    public void add(Connection connection)
            throws GuacamoleException {
        throw new GuacamoleSecurityException("Permission denied.");
    }

    @Override
    public void update(Connection connection)
            throws GuacamoleException {
        throw new GuacamoleSecurityException("Permission denied.");
    }

    @Override
    public void remove(String identifier) throws GuacamoleException {
        throw new GuacamoleSecurityException("Permission denied.");
    }

    @Override
    public void move(String identifier, Directory<String, Connection> directory) 
            throws GuacamoleException {
        throw new GuacamoleSecurityException("Permission denied.");
    }
    

    public Connection putConnection(Connection connection) {
        return connections.put(connection.getName(), connection);
    }
    

    public Connection removeConnection(String identifier) {
        return connections.remove(identifier);
    }

}
