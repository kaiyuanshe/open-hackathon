package com.openhackathon.guacamole;


import java.util.Iterator;

import org.glyptodon.guacamole.protocol.GuacamoleConfiguration;
import org.json.JSONObject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * @foundation transfor the jsonString to GuacamoleConfiguration
 * 
 * @author v-bih
 * 
 * @param  jsonString
 * @return GuacamoleConfiguration
 */
public class Trans2GuacdConfiguration {
	
	private GuacamoleConfiguration configuration ;
	private Logger logger = LoggerFactory.getLogger(Trans2GuacdConfiguration.class.getClass());

	public Trans2GuacdConfiguration(String jsonString) {
			
		configuration = new GuacamoleConfiguration();
		try {
			
			JSONObject json = new JSONObject(jsonString.replace("\\", ""));
			configuration = new GuacamoleConfiguration();
	        Iterator<String> keys = json.keys();  

/**			configuration.setProtocol(json.getString("protocol"));
 *			configuration.setParameter("name", json.getString("name"));
 *			configuration.setParameter("username", json.getString("username"));
 *			configuration.setParameter("password", json.getString("password"));
 *			configuration.setParameter("hostname", json.getString("hostname"));
 *			configuration.setParameter("port", json.getString("port"));
 **/
            /*Automlly set configuration value*/
            while(keys.hasNext()){
                String key = keys.next();
                if (key.equals("displayname")) {
                    continue;
                }
                if (key.equals("protocol")) {
                    configuration.setProtocol(json.getString("protocol"));
                }else {
                    configuration.setParameter(key, json.getString(key));
                }
            }

		} catch (Exception e) {
			logger.error("==================Failed when transfor jsonString to GuacamoleConfiguation  ");
			configuration = new GuacamoleConfiguration();
			e.printStackTrace();			
		}			
	}

	public GuacamoleConfiguration getConfiguration() {
		return configuration;
	}

}
